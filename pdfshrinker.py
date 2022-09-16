#!/usr/bin/env python3
from argparse import ArgumentParser
from multiprocessing import Pool
from shutil import which
from subprocess import run, DEVNULL
from typing import List, Optional, Set, Tuple
import os
import sys

DEFAULT_THREAD_COUNT = 2

ghostscript_name = 'gs'

def resolve_ghostscript_name() -> Optional[str]:
    """ Resolves the name of the GhostScript executable from the `PATH' environment variable. """
    possible_binary_names = [
        'gs',       # Mac / Linux
        'gswin64c', # Windows (64 bits)
        'gswin32c'  # Windows (32 bits)
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

def compute_filesize_reduction(filename_in, filename_out):
    """
        Computes the reduction rate and byte count difference between two files.
        :param filename_in: original file name
        :param filename_out: new file name
        :return: tuple with the reduction rate and byte count difference or (0.0, 0) if the new file is larger than the original
    """
    filesize_in = os.path.getsize(filename_in)
    filesize_out = os.path.getsize(filename_out)
    if filesize_in > filesize_out:
        reduction_rate = 1.0 - filesize_out / filesize_in
        reduction_byte_count = filesize_in - filesize_out
    else:
        reduction_rate = 0.0
        reduction_byte_count = 0
    return (reduction_rate, reduction_byte_count)

def shrink_pdf(filename: str) -> Tuple[str, float, float]:
    """
        Shrinks a PDF file.
        :param filename: PDF filename
        :return: tuple with the PDF filename, reduction rate and byte count reduction
    """
    filename_out = filename + '.gs'
    run_ghostscript(filename, filename_out)
    reduction_rate, reduction_byte_count = compute_filesize_reduction(filename, filename_out)
    if reduction_byte_count > 0:
        os.rename(filename_out, filename)
    else:
        os.remove(filename_out)
    return (filename, reduction_rate, reduction_byte_count)

def shrink_pdfs(pdf_filenames: Set[str], thread_count: int) -> List[Tuple[str, float, float]]:
    """
        Shrinks a set of PDF files.
        :param pdf_filenames: set of PDF filenames
        :param thread_count: number of threads
    """
    results = []
    with Pool(thread_count) as pool:
        results = pool.map(shrink_pdf, pdf_filenames)
    return results

def print_shrink_result(filename: str, reduction_rate: float, reduction_byte_count: int):
    """ Pretty-prints the results of a PDF file shrinking. """
    print("{:.2f} % -- {} ({:,} bytes)".format(-reduction_rate * 100, filename, -reduction_byte_count))

def print_shrink_results(shrink_results: List[Tuple[str, float, float]]):
    """ Pretty-prints the results of many PDF file shrinkings. """
    shrink_results.sort(key=lambda result: result[0])
    for shrink_result in shrink_results:
        print_shrink_result(*shrink_result)

def parse_args():
    parser = ArgumentParser('pdfshrinker')
    parser.add_argument('filenames', type=str, nargs='*', default=['.'], metavar='FILE', help="target directories and PDF files")
    parser.add_argument('--threads', '-X', type=int, default=DEFAULT_THREAD_COUNT, metavar='COUNT', help="number of threads")
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
    print("[+] shrinking {} PDF files using {} threads...".format(len(pdf_filenames), args.threads))
    shrink_results = shrink_pdfs(pdf_filenames, args.threads)
    print_shrink_results(shrink_results)

if __name__ == '__main__':
    main()
