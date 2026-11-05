# SourcecodeSnapshot

![Python](https://img.shields.io/badge/python-3.8%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Latest Release](https://img.shields.io/github/v/release/Betakontext/SourcecodeSnapshot?label=latest%20release)

Lightweight utility to produce a code-only Markdown snapshot of a repository.

This repository contains a single script: `sourcecode_snapshot.py`, which generates
a Markdown file containing a small directory tree excerpt and concatenated source
files (code-only). Optionally the script can also produce a ZIP archive including
the generated Markdown and the selected source files.

Quick links
- Script: `sourcecode_snapshot.py`
- Snapshot output (default): `your_sourcecode_snapshot.md`
- ZIP option: `--zip` / `-z`

## Features

- Includes only selected file extensions and specific filenames.
- Skips common large/irrelevant directories (virtualenvs, models, outputs, recordings).
- Skips very large files (configurable via `--max-size`).
- Produces a short directory tree excerpt (configurable via `--depth`).
- Attempts UTF-8 reading, falls back to latin-1.
- Non-destructive: reads files and writes outputs only.
- CLI options: output filename, ZIP output, dry-run, verbosity, allow additional extensions/names.

## Included file types (default)

Extensions:
- `.py`, `.html`, `.yml`, `.yaml`, `.sh`, `.ps1`, `.txt`, `.service`

Explicit filenames:
- `.env.example`, `.gitignore`, `.dockerignore`, `Dockerfile`, `Makefile`

Default excluded directories:
- `.venv`, `venv`, `__pycache__`, `.git`, `.pytest_cache`, `.mypy_cache`, `models`, `outputs`, `recordings`, `node_modules`, `dist`, `build`

## Installation

No installation required. Copy `sourcecode_snapshot.py` to your project root or clone this repository:

```bash
git clone https://github.com/Betakontext/SourcecodeSnapshot.git
cd SourcecodeSnapshot

(Optional) Make executable:
BASH
Kopieren

chmod +x sourcecode_snapshot.py

Usage

Place sourcecode_snapshot.py in the project root (or install it to your PATH) and run:
BASH
Kopieren

python3 sourcecode_snapshot.py

Common options:

    --out, -o: Output markdown filename (default your_sourcecode_snapshot.md).
    --zip, -z: Optional ZIP output path; if provided, create ZIP containing markdown and source files.
    --max-size: Maximum file size (bytes) to include (default 30 MiB).
    --depth: Directory tree excerpt depth (default 2).
    --dry-run: Show what would be included, do not write files.
    --verbose, -v: Verbose output.
    --allow-ext: Add an allowed extension (e.g. --allow-ext .md), can be used multiple times.
    --allow-name: Add an allowed filename (e.g. --allow-name README.md), can be used multiple times.

Example:
BASH
Kopieren

# default run
python3 sourcecode_snapshot.py

# custom output and zip
python3 sourcecode_snapshot.py --out project_snapshot.md --zip project_snapshot.zip

# dry-run to check without writing
python3 sourcecode_snapshot.py --dry-run --verbose

Output

    your_sourcecode_snapshot.md (or your chosen --out) — a Markdown file that begins with
    a small directory tree excerpt and continues with the contents of each included source file,
    each within a fenced code block.

    If --zip is provided, a ZIP archive is created that contains the Markdown file and the included source files preserving relative paths.

CI integration (optional)

You can run the script in CI to produce artifacts or commit snapshots to a branch. Example GitHub Actions badge (replace with actual workflow if you add it):

    CI badge placeholder (add a workflow and replace workflow-name):


    https://github.com/<your-org>/<your-repo>/actions/workflows/<workflow-file>.yaml/badge.svg



Contributing

Contributions welcome. Suggestions:

    Add more CLI options (output formats: tar.gz, commit to branch).
    Add filtering by .gitignore or by git tracked files only.
    Add unit tests (pytest) for gather and tree functionality.
    Windows path handling improvements and encoding tests.

Please open issues or PRs.
License

This project is licensed under the MIT License — see the accompanying LICENSE file for details.

If this helped, star the repo ⭐
