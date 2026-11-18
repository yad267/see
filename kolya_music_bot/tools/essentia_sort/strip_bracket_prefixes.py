#!/usr/bin/env python3
"""
Strip Cursor/agent technical prefixes like "[0 ONO] " from filenames.

- Only renames in place (no move to other genre folders).
- Does NOT modify ID3 tags.
- Does NOT remove user markers that are part of the real title
  (e.g. "ОНО Лена Illusion..." stays as-is after prefix strip).
- Default: dry-run. Pass --apply to rename.

Example:
  python strip_bracket_prefixes.py --root "/Users/Sputnik/Music/МУЗЫКА ПРОБА/ГОТОВО МУЗЫКА"
  python strip_bracket_prefixes.py --root "..." --apply
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

AUDIO_EXT = {".mp3", ".m4a", ".flac", ".wav", ".ogg", ".aac", ".aiff", ".aif"}

# One or more leading [anything] blocks + following spaces
PREFIX_RE = re.compile(r"^(?:\[[^\]]*\]\s*)+")


def unique_path(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    if not candidate.exists():
        return candidate
    stem = Path(filename).stem
    ext = Path(filename).suffix
    for i in range(1, 10000):
        alt = directory / f"{stem}_{i}{ext}"
        if not alt.exists():
            return alt
    raise RuntimeError(f"Cannot find free name for {filename} in {directory}")


def clean_name(name: str) -> str | None:
    """Return new filename if prefix stripped, else None (no change)."""
    if not PREFIX_RE.match(name):
        return None
    new_name = PREFIX_RE.sub("", name, count=1).strip()
    # safety: never empty
    if not new_name or new_name.startswith("."):
        return None
    if new_name == name:
        return None
    return new_name


def main() -> int:
    ap = argparse.ArgumentParser(description="Strip [bracket] prefixes from audio filenames")
    ap.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Folder to process recursively",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Actually rename (default is dry-run)",
    )
    ap.add_argument(
        "--log",
        type=Path,
        default=None,
        help="Log file path (default: <root>/log_strip_prefixes.txt)",
    )
    args = ap.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1

    log_path = args.log or (root / "log_strip_prefixes.txt")
    lines: list[str] = []
    planned = 0
    skipped = 0
    errors = 0

    mode = "APPLY" if args.apply else "DRY-RUN"
    header = f"mode={mode}\nroot={root}\n"
    print(header.strip())
    lines.append(header)

    for dirpath, _dirnames, filenames in os.walk(root):
        directory = Path(dirpath)
        for filename in sorted(filenames):
            path = directory / filename
            if path.suffix.lower() not in AUDIO_EXT:
                continue
            new_name = clean_name(filename)
            if not new_name:
                skipped += 1
                continue

            dest = unique_path(directory, new_name)
            # if unique_path added _1 because conflict with different file
            final_name = dest.name
            msg = f'"{filename}" -> "{final_name}"'
            print(msg)
            lines.append(msg)
            planned += 1

            if args.apply:
                try:
                    # avoid no-op if somehow same path
                    if path.resolve() != dest.resolve():
                        os.rename(path, dest)
                except OSError as exc:
                    err = f"ERROR: {filename}: {exc}"
                    print(err, file=sys.stderr)
                    lines.append(err)
                    errors += 1

    summary = (
        f"\nsummary: planned={planned} skipped_no_prefix={skipped} errors={errors} mode={mode}"
    )
    print(summary.strip())
    lines.append(summary)

    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"log: {log_path}")
    if not args.apply:
        print("Dry-run only. Re-run with --apply to rename.")
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
