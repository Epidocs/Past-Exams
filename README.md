# Epidocs / Past Exams

[![Build Status](https://travis-ci.com/Epidocs/Past-Exams.svg?branch=master)](https://travis-ci.com/Epidocs/Past-Exams)

Past subjects and other files, for the benefit of EPITA students.

Visit the website: [past-exams.epidocs.eu](https://past-exams.epidocs.eu/)


## Contributing

To contribute, you can fork this project, add files and then open a pull request.

### Compress your files!

When adding files, using the `pdfshrink.py' script to compress them.

The script is made to be run on Linux, and it requires Python 3.5+.

Usage: `pdfshrink.py [path]`

The optional `path` parameter can be:
- The path to the pdf file to compress.
- The path to a folder to search pdf files in.
If omitted, the script will search for pdfs in the current folder and its sub-folders.


## Continuous Integration builds

Powered by Travis CI.

At every push to `master`, the PHP script `deploy.php` is executed to generate the website infos and deploy the result to `gh-pages`.

- "/_assets/" content is moved to the root directory at the end of the script
