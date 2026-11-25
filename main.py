#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Deliver the finished front page of the 25 November 2026 edition.

The rendered newspaper page ships in this repository as entry.png. The
harness expects the program to place it at /output/entry.png, so this
script performs a verified byte-for-byte copy and nothing else.
"""

import os
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
PAGE_FILE = REPO_DIR / "entry.png"
BLOCK = 128 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def check_page(page: Path) -> None:
    """Refuse to deliver anything that is not a PNG image."""
    with page.open("rb") as src:
        if src.read(len(PNG_MAGIC)) != PNG_MAGIC:
            raise SystemExit(f"{page.name} is not a PNG file")


def deliver(page: Path, destination: Path) -> int:
    """Stream page to destination; return the number of bytes written."""
    total = 0
    with page.open("rb") as src, destination.open("wb") as dst:
        while block := src.read(BLOCK):
            dst.write(block)
            total += len(block)
    expected = page.stat().st_size
    if total != expected:
        raise SystemExit(f"copy incomplete: wrote {total} of {expected} bytes")
    return total


def main() -> None:
    check_page(PAGE_FILE)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    deliver(PAGE_FILE, out_dir / "entry.png")


if __name__ == "__main__":
    main()
