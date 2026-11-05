#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sourcecode_snapshot.py

Create a Markdown snapshot of a repository (code-only) and optionally package it as a ZIP.

Outputs:
 - <out_md> (default: your_sourcecode_snapshot.md)
 - optional ZIP archive containing the Markdown and the selected source files

Features:
 - Includes only selected file extensions and specific filenames.
 - Skips common large/irrelevant directories and very large files.
 - Produces a short directory tree excerpt (configurable depth).
 - Attempts UTF-8 read, falls back to latin-1.
 - Non-destructive: reads files and writes outputs only.
 - CLI with flags: --out, --zip, --max-size, --depth, --dry-run, --verbose

Usage:
    python3 sourcecode_snapshot.py [--out my_snapshot.md] [--zip my_snapshot.zip] [--dry-run]

Example:
    python3 sourcecode_snapshot.py --out project_snapshot.md --zip project_snapshot.zip
"""
from __future__ import annotations
import argparse
import os
import sys
import time
import zipfile
import stat
from pathlib import Path
from typing import List, Iterable, Tuple

# --------------------
# Default configuration
# --------------------
DEFAULT_OUT_MD = "your_sourcecode_snapshot.md"
DEFAULT_ALLOWED_EXTS = {".py", ".html", ".yml", ".yaml", ".sh", ".ps1", ".txt", ".service"}
DEFAULT_ALLOWED_NAMES = {".env.example", ".gitignore", ".dockerignore", "Dockerfile", "Makefile"}
DEFAULT_EXCLUDE_DIRS = {
    ".venv", "venv", "__pycache__", ".git", ".pytest_cache", ".mypy_cache",
    "models", "outputs", "recordings", "node_modules", "dist", "build"
}
DEFAULT_MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MiB
DEFAULT_TREE_DEPTH = 2

# --------------------
# Utility functions
# --------------------
def is_allowed_file(path: Path, allowed_exts: set, allowed_names: set) -> bool:
    name = path.name
    if name in allowed_names:
        return True
    if path.suffix.lower() in allowed_exts:
        return True
    return False

def should_skip_dir(dirpath: Path, exclude_dirs: set) -> bool:
    return dirpath.name in exclude_dirs

def gather_files(root: Path, allowed_exts: set, allowed_names: set,
                 exclude_dirs: set, max_file_size: int, out_md: Path, verbose: bool=False) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # filter dirs in-place to avoid walking excluded dirs
        dirnames[:] = [d for d in dirnames if not should_skip_dir(Path(dirpath) / d, exclude_dirs)]
        for fn in filenames:
            p = Path(dirpath) / fn
            # skip the output markdown if it exists from previous run
            try:
                if p.resolve() == out_md.resolve():
                    if verbose:
                        print(f"Skipping output file itself: {p}")
                    continue
            except Exception:
                # path resolution may fail for broken symlinks; just continue
                pass
            # skip symlinks (do not follow)
            try:
                if p.is_symlink():
                    if verbose:
                        print(f"Skipping symlink: {p}")
                    continue
            except Exception:
                continue
            # skip very large files
            try:
                if p.stat().st_size > max_file_size:
                    if verbose:
                        print(f"Skipping large file: {p} ({p.stat().st_size} bytes)")
                    continue
            except Exception:
                # skip unreadable files
                if verbose:
                    print(f"Skipping unreadable file: {p}")
                continue
            if is_allowed_file(p, allowed_exts, allowed_names):
                files.append(p)
    files.sort()
    return files

def make_tree_listing(root: Path, depth: int = DEFAULT_TREE_DEPTH) -> str:
    lines: List[str] = []
    def walk(p: Path, prefix: str, current_depth: int):
        if current_depth > depth:
            return
        try:
            entries = sorted([e for e in p.iterdir()])
        except Exception:
            return
        for i, e in enumerate(entries):
            connector = "└── " if i == len(entries)-1 else "├── "
            lines.append(f"{prefix}{connector}{e.name}")
            if e.is_dir():
                ext_prefix = prefix + ("    " if i == len(entries)-1 else "│   ")
                walk(e, ext_prefix, current_depth + 1)
    lines.append(f"{root.name}/")
    walk(root, "", 1)
    return "\n".join(lines)

def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return f"# Could not read file {path}\n"
    except Exception:
        return f"# Could not read file {path}\n"

def write_markdown(tree: str, files: List[Path], out_md: Path, project_name: str, timestamp: str) -> None:
    header = f"# {project_name} - snapshot\n\n"
    header += f"Created: {timestamp}\n\n"
    header += "## Directory tree (excerpt)\n\n"
    header += "```\n" + tree + "\n```\n\n"
    header += "## Included source files (code-only snapshot)\n\n"
    header += ("The following files are included in the snapshot. "
               "Each filename is followed by its content.\n\n")
    with out_md.open("w", encoding="utf-8") as f:
        f.write(header)
        for p in files:
            rel = p.relative_to(out_md.parent)
            f.write(f"\n---\n\n### {rel}\n\n")
            lang = p.suffix.lstrip(".")
            f.write(f"```{lang}\n")
            content = read_text_file(p)
            f.write(content)
            if not content.endswith("\n"):
                f.write("\n")
            f.write("```\n")
    print(f"Wrote markdown snapshot: {out_md}")

def add_file_to_zip(z: zipfile.ZipFile, path: Path, arcname: str) -> None:
    zi = zipfile.ZipInfo(arcname)
    st = path.stat()
    # preserve permission bits
    zi.external_attr = (st.st_mode & 0xFFFF) << 16
    zi.date_time = time.localtime(st.st_mtime)[:6]
    with path.open("rb") as f:
        data = f.read()
    z.writestr(zi, data)

def create_zip_archive(zip_path: Path, md_path: Path, files: List[Path], root: Path, verbose: bool=False) -> None:
    if zip_path.exists():
        raise FileExistsError(f"{zip_path} already exists")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # add markdown first
        add_file_to_zip(z, md_path, md_path.name)
        for p in files:
            rel = p.relative_to(root)
            arcname = str(rel).replace(os.sep, "/")
            if verbose:
                print(f"Adding to zip: {arcname}")
            add_file_to_zip(z, p, arcname)
    print(f"Created zip archive: {zip_path}")

# --------------------
# CLI
# --------------------
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Create a code-only Markdown snapshot and optional ZIP")
    ap.add_argument("--out", "-o", default=DEFAULT_OUT_MD, help="Output markdown filename (default: %(default)s)")
    ap.add_argument("--zip", "-z", dest="zipout", default=None, help="Optional ZIP output path; if provided, create ZIP containing markdown and source files")
    ap.add_argument("--max-size", type=int, default=DEFAULT_MAX_FILE_SIZE, help="Maximum file size (bytes) to include (default: %(default)s)")
    ap.add_argument("--depth", type=int, default=DEFAULT_TREE_DEPTH, help="Directory tree excerpt depth (default: %(default)s)")
    ap.add_argument("--dry-run", action="store_true", help="Dry run: show what would be included, do not write files")
    ap.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    ap.add_argument("--project-name", default=None, help="Project name to show in header (defaults to current directory name)")
    ap.add_argument("--allow-ext", action="append", help="Additional allowed extension (e.g. --allow-ext .md). Can be passed multiple times.")
    ap.add_argument("--allow-name", action="append", help="Additional allowed filename (e.g. --allow-name README.md). Can be passed multiple times.")
    return ap.parse_args()

def main() -> int:
    args = parse_args()
    root = Path.cwd()
    out_md = root / args.out
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    project_name = args.project_name or root.name

    allowed_exts = set(DEFAULT_ALLOWED_EXTS)
    allowed_names = set(DEFAULT_ALLOWED_NAMES)
    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
    max_file_size = args.max_size
    depth = args.depth
    dry_run = args.dry_run
    verbose = args.verbose

    if args.allow_ext:
        for e in args.allow_ext:
            if not e.startswith("."):
                e = "." + e
            allowed_exts.add(e.lower())
    if args.allow_name:
        for n in args.allow_name:
            allowed_names.add(n)

    if verbose:
        print(f"Root: {root}")
        print(f"Out markdown: {out_md}")
        if args.zipout:
            print(f"ZIP output: {args.zipout}")
        print(f"Allowed extensions: {sorted(allowed_exts)}")
        print(f"Allowed names: {sorted(allowed_names)}")
        print(f"Exclude dirs: {sorted(exclude_dirs)}")
        print(f"Max file size: {max_file_size}")
        print(f"Tree depth: {depth}")
        print(f"Dry run: {dry_run}")

    files = gather_files(root, allowed_exts, allowed_names, exclude_dirs, max_file_size, out_md, verbose=verbose)

    if not files:
        print("No source files found with the allowed patterns.", file=sys.stderr)
        return 3

    tree = make_tree_listing(root, depth)

    # Dry-run: print summary and exit
    if dry_run:
        print("\nDRY RUN: files that would be included:")
        for p in files:
            print(f" - {p.relative_to(root)}")
        print("\nDirectory tree excerpt:\n")
        print(tree)
        return 0

    # Write markdown
    write_markdown(tree, files, out_md, project_name, timestamp)

    # Optionally create zip
    if args.zipout:
        zip_path = Path(args.zipout)
        try:
            create_zip_archive(zip_path, out_md, files, root, verbose=verbose)
        except Exception as e:
            print(f"Failed to create zip: {e}", file=sys.stderr)
            return 4

    print("\nDone.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
