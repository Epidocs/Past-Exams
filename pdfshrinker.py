import os
from sys import argv
from shutil import which
from subprocess import run

walkpath = argv[1] if len(argv) >= 2 else '.'

if which('gswin64c') is not None: gs = 'gswin64c' # Windows 64-bit
elif which('gswin32c') is not None: gs = 'gswin32c' # Windows 32-bit
elif which('gs') is not None: gs = 'gs' # Other
else: sys.exit('Error: Could not find GhostScript!')

def shrink_file(root, filename):
	f, e = os.path.splitext(filename)
	if e == '.pdf':
		path = os.path.join(root, filename)
		npath = os.path.join(root, f + '_shrink' + e)

		run([gs, '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', '-dPDFSETTINGS=/ebook' ,'-sOutputFile=' + npath, path])
		if os.path.isfile(npath):
			size_pre = os.path.getsize(path) # File size before shrinking
			size_post = os.path.getsize(npath) # File size after shrinking

			reduce_rate, reduce_bytes = (0.0, 0)

			if size_post < size_pre:
				# The new file is smaller than the existing one; keep it
				os.remove(path)
				os.rename(npath, path)

				reduce_rate = 1.0 - size_post / size_pre
				reduce_bytes = size_pre - size_post
			else:
				# The new file is larger than the existing one; delete it
				os.remove(npath)

			print("shrink_file: {:.2f} % -- {} ({:,} bytes)".format(-reduce_rate * 100, path, -reduce_bytes))

if os.path.isfile(walkpath):
	root, filename = os.path.split(walkpath)
	shrink_file(root, filename)
else:
	for root, dirs, files in os.walk(walkpath, topdown=False):
		for filename in files:
			shrink_file(root, filename)
