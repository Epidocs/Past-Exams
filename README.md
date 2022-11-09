# Epidocs / Past Exams

[![Build Status](https://travis-ci.com/Epidocs/Past-Exams.svg?branch=master)](https://travis-ci.com/Epidocs/Past-Exams)

Past subjects and other files, for the benefit of EPITA students.

Visit the website: [past-exams.epidocs.eu](https://past-exams.epidocs.eu/)

## Contributing

To contribute, you can fork this project, add files and then open a pull request.

### Compress your files!

When adding files, please use the `pdfshrinker.py` script at the root of this repository to compress them!

The script is made to be run on any OS. It requires Python 3.5+ and [GhostScript](https://www.ghostscript.com/).

Usage: `pdfshrinker [-h] [--threads count] [path [path ...]]`

The optional `path` argument can be either paths to one or many PDF files and/or directories to search PDF files in.
If omitted, the script will search for PDFs in the current folder and its sub-directories.

You can set the number of threads using the `--threads` or `-X` optional argument. Default is 2.

Example: `python3 pdfshrinker.py -X 4 ./S3/MCQs`

In this example, the script will use 4 threads to shrink the PDF files of the `S3/MCQs` directory and its sub-directories.

## Continuous Integration builds

Powered by Travis CI.

At every push to `master`, the PHP script `deploy.php` is executed to generate the website infos and deploy the result to `gh-pages`.

- `/_assets/` content is moved to the root directory at the end of the script.
