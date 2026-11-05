# sourcecode-snapshot

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

## Usage

Place `sourcecode_snapshot.py` in the project root (or install it to your PATH) and run:

```bash
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

Configuration

Edit the script constants or use CLI flags to adapt behavior:

    ALLOWED_EXTS — extensions to include
    ALLOWED_NAMES — explicit filenames to include
    EXCLUDE_DIRS — top-level directories to skip
    MAX_FILE_SIZE — maximum file size in bytes to include
    TREE_DEPTH — depth of the tree excerpt

Recommended workflow / CI

    Add the script to your repo, run it in CI to produce an artifact, or run locally to create a compact code snapshot for review/sharing.
    Use --dry-run in CI checks to ensure the intended files are selected.
    If you need an automatic snapshot on tag or release, add a GitHub Actions job that runs the script and uploads the markdown/zip as artifacts.

Contributing

Contributions welcome. Suggestions:

    Add more CLI options (output formats: tar.gz, commit to branch).
    Add filtering by gitignore or by git tracked files only.
    Add unit tests (pytest) for gather and tree functionality.
    Windows path handling improvements and encoding tests.

Please open issues or PRs.
License

This project is licensed under the MIT License — see the accompanying LICENSE file for details.
