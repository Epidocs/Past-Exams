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
			if os.path.getsize(npath) < os.path.getsize(path):
				# The new file is smaller than the existing one; keep it
				os.remove(path)
				os.rename(npath, path)
			else:
				# The new file is larger than the existing one; delete it
				os.remove(npath)

if os.path.isfile(walkpath):
	root, filename = os.path.split(walkpath)
	shrink_file(root, filename)
else:
	for root, dirs, files in os.walk(walkpath, topdown=False):
		for filename in files:
			shrink_file(root, filename)
