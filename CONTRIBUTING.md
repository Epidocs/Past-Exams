# Contributing guidelines

## How to contribute?

- Fork the repository
- Prepare your files: check the naming and compress them
- Upload your files in the folder where they belong
- Create a new pull request to propose your changes

You can contribute directly via Github,
or you can `git clone` your fork on your computer.

## Adding new files

### File naming rules

**No pull request will be accepted if these rules are not respected.**

- Files **must** be named in English.
- File names **must** be lowercase.
- File names **must** be follow this format:
  - For most exams: `<Type>-<Promotion>-<Semester>-<Discipline>[-<Optional_Info>][-<Language>].<Format>`
  - For MCQs: `<Type>-<Promotion>-<Semester>-<MCQ#>[-<Optional_Info>][-<Language>].<Format>`

Examples:
- `midterm-2023-s2-algo-answer_sheet-en.pdf`
- `final-2021-s2-maths-subject-fr.pdf`
- `retake-2020-s3-archi-correction-fr.pdf`
- `mcq-2022#-s2-02-correction.csv`

File names format details:
- **`Type`** can be: `midterm`, `final`, `retake`, `mcq`, ...
- **`Promotion`** is the 4-digit promotion year: `2021`, `2022`, `2023`, ...
  - This can be optionally folowed by the symbol `#`: `2021#`, `2022#`, `2023#`, ...
- **`Semester`** is the formatted semester code: `s1`, `s2`, `s3`, `s4`, ...
- - **`Discipline`** is the shortened discipline name: `maths`, `algo`, `phys`, `elec`, `archi`, `te`, `cie`, `tim`
  - **`MCQ#`** is the 2-digit MCQ number: `01`, `02`, `03`, ...
- **`Optional_Info`** is aditional information on the file. This must not contain a dash (`-`).
  - This can be: `subject`, `correction`, `answer_sheet`, ...
- **`Language`** is the 2-letter language code ([ISO 639-1 code](https://en.wikipedia.org/wiki/ISO_639-1)): `fr`, `en`, ...
- **`Format`** is the file format: `pdf`, `csv`, `py`, ...

### Compress your files

Compressing your files is highly recommended and appreciated. You can run the `pdfshrink.py` script to do so.

Requirements:
- Python 3.5+
- GhostScript

Usage: `python pdfshrink.py [path]`
- The optional `path` parameter can be:
  - The path to the pdf file to compress.
  - The path to a folder to search pdf files in.
- If omitted, the script will search for pdfs in the current folder and its sub-folders.
