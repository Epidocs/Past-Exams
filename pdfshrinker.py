#!/usr/bin/env python3

from argparse import ArgumentParser
from multiprocessing import Pool
from shutil import which
from subprocess import run, DEVNULL
from typing import List, Optional, Set, Tuple
import os
import sys

DEFAULT_THREAD_COUNT = 2

# GhostScript executable name
gs_exec = "gs"

def get_gs_exec() -> Optional[str]:
	"""
		Resolves the name of the GhostScript executable

		:return: the executable name of GhostScript or None if it was not found
	"""

	# Possible GhostScript executable names
	executable_names = [
		'gswin64c', # Windows 64-bit
		'gswin32c', # Windows 32-bit
		'gs'        # Other
	]

	# Search for the executable
	for exec_name in executable_names:
		if which(exec_name) is not None:
			return exec_name

	return None

def is_pdf(filename: str) -> bool:
	"""
		Determines if a filename has a PDF extension

		:param filename: the filename
		:return: True if the filename has a '.pdf' extension
	"""

	extension = os.path.splitext(filename)[1]
	return extension == '.pdf'

def collect_pdfs(roots: List[str]) -> Set[str]:
	"""
		Collects all the PDF files from the specified
		root files and their sub-directories if any

		:param roots: the paths to the root directories and/or PDF files
		:return: a set containing the filenames of every PDF file
	"""

	pdfs = set()

	for root in roots:
		if os.path.isdir(root):
			for root, dirs, files in os.walk(root):
				for file in files:
					if is_pdf(file):
						pdfs.add(os.path.join(root, file))

				pdfs.union(collect_pdfs(dirs))
		elif is_pdf(root):
			pdfs.add(root)

	return pdfs

def shrink_file(filename: str) -> Tuple[str, float, float]:
	"""
		Shrinks a PDF file using GhostScript

		:param filename: the filename of the PDF file
        :return: the result in terms of filesize reduction
	"""

	global gs_exec

	# Temporary filename for the GhostScript output
	filename_gs_out = filename + '.gs'

	# Run GhostScript on the PDF file
	status = run([
		gs_exec,
		'-q',
		'-dNOPAUSE',
		'-dBATCH',
		'-sDEVICE=pdfwrite',
		'-dPDFSETTINGS=/ebook',
		'-sOutputFile=' + filename_gs_out,
		filename
	], check=True, stdout=DEVNULL)

	# Filesize before shrinking
	size_pre = os.path.getsize(filename)

	# Filesize after shrinking
	size_post = os.path.getsize(filename_gs_out)

	# Filesize reduction in percentage and raw byte count
	reduce_rate, reduce_byte_count = (0.0, 0)

	if size_post < size_pre:
		# The new file is smaller than the existing one; keep it
		os.remove(filename)
		os.rename(filename_gs_out, filename)

		reduce_rate = 1.0 - size_post / size_pre
		reduce_byte_count = size_pre - size_post
	else:
		# The new file is larger than the existing one; delete it
		os.remove(filename_gs_out)

	return (filename, reduce_rate, reduce_byte_count)

def shrink_files(pdfs: Set[str], thread_count: int) -> List[Tuple[str, float, float]]:
	"""
		Shrinks a collection of PDF files

		:param pdfs: a set containing the filenames of the PDF files to shrink
		:param thread_count: number of processes to use
		:return: the results (in terms of filesize reduction) for each file
	"""

	results = []

	with Pool(thread_count) as pool:
		results = pool.map(shrink_file, pdfs)

	return results

def print_shrink_results(results: List[Tuple[str, float, float]]):
	# sort the results by filename
	results.sort(key=lambda result: result[0])

	for filename, reduce_rate, reduce_byte_count in results:
		print("shrink_file: {:.2f} % -- {} ({:,} bytes)".format(-reduce_rate * 100, filename, -reduce_byte_count))

def main():
	global gs_exec
	gs_exec = get_gs_exec()

	if gs_exec is not None:
		parser = ArgumentParser("pdfshrinker")
		parser.add_argument("path", type=str, nargs='*', default=['.'], help="Target files and directories")
		parser.add_argument("--threads", "-X", type=int, default=DEFAULT_THREAD_COUNT, metavar="count", help="Number of threads")

		args = parser.parse_args()

		pdfs = collect_pdfs(args.path)

		print("[+] shrinking {} PDF files using {} threads...".format(len(pdfs), args.threads))
		results = shrink_files(pdfs, args.threads)

		print_shrink_results(results)
	else:
		sys.exit("Error: unable to find GhostScript executable in PATH")

if __name__ == "__main__":
	main()
