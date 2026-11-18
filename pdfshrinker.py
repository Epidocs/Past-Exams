#!/usr/bin/env python3
from argparse import ArgumentParser
from functools import partial
from multiprocessing import Pool
from shutil import copyfile, which
from subprocess import run, DEVNULL
from tempfile import TemporaryDirectory
from typing import List, Optional, Set, Tuple
import math
import os
import sys

DEFAULT_THREAD_COUNT = 2

# A shrink is kept only if it saves more than BASE * log10(size / BASE) bytes,
# with BASE = 10 KB (no minimum at or below BASE).
MIN_REDUCTION_BASE = 10 * 1024

ghostscript_name = 'gs'

def resolve_ghostscript_name() -> Optional[str]:
    """ Resolves the name of the GhostScript executable from the `PATH' environment variable. """
    possible_binary_names = [
        'gs',       # Mac / Linux
        'gswin64c', # Windows (64 bits)
        'gswin32c', # Windows (32 bits)
    ]
    for binary in possible_binary_names:
        if which(binary) is not None:
            return binary

def is_hidden(filename: str) -> bool:
    """ Determines whether a file is hidden (UNIX definition). """
    filename = os.path.basename(filename)
    return filename.startswith('.')

def is_visible(filename: str) -> bool:
    """ Determines whether a file is not hidden (UNIX definition). """
    return not is_hidden(filename)

def is_pdf(filename: str) -> bool:
    """ Determines whether a file has a PDF extension. """
    _, extension = os.path.splitext(filename)
    return is_visible(filename) and extension == '.pdf'

def collect_pdfs(root: str) -> Set[str]:
    """
        Collects all the PDF files names from the given root file.
        :param root: filename of a PDF file or directory to search PDF files in
        :return: all of the PDF files names that were found from `root'
    """
    pdf_filenames = set()
    if os.path.isdir(root):
        for filename in filter(is_visible, os.listdir(root)):
            filepath = os.path.join(root, filename)
            pdf_filenames = pdf_filenames.union(collect_pdfs(filepath))
    elif is_pdf(root):
        pdf_filenames.add(root)
    return pdf_filenames

def run_ghostscript(filename_in, filename_out):
    """
        Runs the GhostScript executable on a PDF file.
        :param filename_in: input PDF file name
        :param filename_out: output PDF file name
    """
    global ghostscript_name
    run([
        ghostscript_name,
        '-q',
        '-dNOPAUSE',
        '-dBATCH',
        '-sDEVICE=pdfwrite',
        '-dPDFSETTINGS=/ebook',
        '-sOutputFile=' + filename_out,
        filename_in
    ], check=True, stdout=DEVNULL)

def compute_min_reduction(filesize: int, base: int = MIN_REDUCTION_BASE) -> float:
    """ Minimum bytes a shrink must save for a file of this size (0 if base is 0). """
    if base <= 0 or filesize <= base:
        return 0
    return base * math.log10(filesize / base)

def compute_filesize_reduction(filename_in, filename_out, base: int = MIN_REDUCTION_BASE):
    """
        Computes the reduction rate and byte count difference between two files.
        :return: tuple with the reduction rate and byte count difference or (0.0, 0) if below the threshold
    """
    filesize_in = os.path.getsize(filename_in)
    filesize_out = os.path.getsize(filename_out)
    reduction_byte_count = filesize_in - filesize_out
    if reduction_byte_count <= compute_min_reduction(filesize_in, base):
        return (0.0, 0)
    return (reduction_byte_count / filesize_in, reduction_byte_count)

def overwrite_file(filename_in, filename_out):
    """
        Replaces a file with another one, and removes the source file.
        Tries an atomic replace first. If it fails (different filesystems, read-only directory...),
        falls back to overwriting the file in place, which only requires write access to the file itself.
        :param filename_in: source file name
        :param filename_out: file name to overwrite
    """
    try:
        os.replace(filename_in, filename_out)
    except OSError:
        copyfile(filename_in, filename_out)
        os.remove(filename_in)

def resolve_output_filename(filename: str, output_dir: str) -> str:
    """
        Resolves the output file name in the output directory, preserving the relative path of the input file.
        :param filename: input PDF filename
        :param output_dir: output directory
        :return: output PDF filename
    """
    relative_filename = os.path.relpath(filename)
    if relative_filename.startswith(os.pardir + os.sep) or relative_filename == os.pardir:
        raise ValueError("file is outside the current directory, cannot preserve its relative path")
    return os.path.join(output_dir, relative_filename)

def shrink_pdf(filename: str, output_dir: Optional[str] = None, base: int = MIN_REDUCTION_BASE) -> Tuple[str, float, float, Optional[str]]:
    """
        Shrinks a PDF file. Never raises: failures are returned as an error message.
        :param filename: PDF filename
        :param output_dir: output directory, or None to overwrite the PDF file in place
        :return: tuple with the PDF filename, reduction rate, byte count reduction and error message (or None)
    """
    try:
        if output_dir is not None:
            # Export mode: the input file is left untouched
            filename_out = resolve_output_filename(filename, output_dir)
            os.makedirs(os.path.dirname(filename_out), exist_ok=True)
            run_ghostscript(filename, filename_out)
            reduction_rate, reduction_byte_count = compute_filesize_reduction(filename, filename_out, base)
            if reduction_byte_count == 0:
                # Not smaller: export the original file instead
                copyfile(filename, filename_out)
        else:
            # Write to a temporary directory: the PDF's directory may not be writable
            with TemporaryDirectory() as tmpdir:
                filename_out = os.path.join(tmpdir, 'out.pdf')
                run_ghostscript(filename, filename_out)
                reduction_rate, reduction_byte_count = compute_filesize_reduction(filename, filename_out, base)
                if reduction_byte_count > 0:
                    overwrite_file(filename_out, filename)
        return (filename, reduction_rate, reduction_byte_count, None)
    except Exception as error:
        return (filename, 0.0, 0, "{}: {}".format(type(error).__name__, error))

def shrink_pdfs(pdf_filenames: Set[str], thread_count: int, output_dir: Optional[str] = None, base: int = MIN_REDUCTION_BASE) -> List[Tuple[str, float, float, Optional[str]]]:
    """
        Shrinks a set of PDF files.
        :param pdf_filenames: set of PDF filenames
        :param thread_count: number of threads
        :param output_dir: output directory, or None to overwrite the PDF files in place
    """
    results = []
    with Pool(thread_count) as pool:
        results = pool.map(partial(shrink_pdf, output_dir=output_dir, base=base), pdf_filenames)
    return results

def print_shrink_result(result: Tuple[str, float, float, Optional[str]]):
    """ Pretty-prints the results of a PDF file shrinking. """
    filename, reduction_rate, reduction_byte_count, error = result
    if error is not None:
        print("FAILED -- {} ({})".format(filename, error), file=sys.stderr)
        return
    print("{:.2f} % -- {} ({:,} bytes)".format(-reduction_rate * 100, filename, -reduction_byte_count))

def print_shrink_results(results: List[Tuple[str, float, float, Optional[str]]]):
    """ Pretty-prints the results of many PDF file shrinkings. """
    results.sort(key=lambda result: result[0])
    for result in results:
        print_shrink_result(result)

def parse_args():
    parser = ArgumentParser('pdfshrinker')
    parser.add_argument('filenames', type=str, nargs='*', default=['.'], metavar='FILE', help="target directories and PDF files")
    parser.add_argument('--threads', '-X', type=int, default=DEFAULT_THREAD_COUNT, metavar='COUNT', help="number of threads")
    parser.add_argument('--output-dir', '-o', type=str, default=None, metavar='DIR', help="write shrunk PDFs to this directory, preserving relative paths, instead of overwriting the originals")
    parser.add_argument('--min-reduction-base', type=int, default=MIN_REDUCTION_BASE, metavar='BYTES', help="base of the minimum reduction threshold in bytes, 0 keeps any reduction (default: %(default)s)")
    return parser.parse_args()

def main():
    global ghostscript_name
    ghostscript_name = resolve_ghostscript_name()
    if ghostscript_name is None:
        print("Could not find GhostScript executable in PATH.", file=sys.stderr)
        sys.exit(1)
    args = parse_args()
    pdf_filenames = set()
    for filename in args.filenames:
        pdf_filenames = pdf_filenames.union(collect_pdfs(filename))
    print("[+] shrinking {} PDF files using up to {} threads...".format(len(pdf_filenames), args.threads))
    shrink_results = shrink_pdfs(pdf_filenames, args.threads, args.output_dir, args.min_reduction_base)
    print_shrink_results(shrink_results)

if __name__ == '__main__':
    main()
