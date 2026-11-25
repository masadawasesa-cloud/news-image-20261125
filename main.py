#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Entry program for the 25 November 2026 edition of The World in One Day.

The finished front page travels with this repository as ``entry.png``.
Running this program publishes it to the harness output directory,
proving on the way that the source really is a PNG, that it respects
the competition's one-mebibyte cap, and that the published bytes hash
to exactly the source's digest.
"""

import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / "entry.png"
CHUNK = 256 * 1024
SIZE_CAP = 1_048_576  # the gate allows at most 1 MiB
PNG_SIGNATURE = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))


def page_digest(path):
    """SHA-256 of a file, read in blocks so memory stays flat."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def publish(source, target):
    """Copy source onto target; return the number of bytes moved."""
    moved = 0
    with source.open("rb") as reader, target.open("wb") as writer:
        for block in iter(lambda: reader.read(CHUNK), b""):
            writer.write(block)
            moved += len(block)
    return moved


def main():
    size = PAGE.stat().st_size
    if size > SIZE_CAP:
        sys.exit(f"entry.png is {size} bytes, over the {SIZE_CAP}-byte cap")
    with PAGE.open("rb") as handle:
        if handle.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
            sys.exit("entry.png does not start with the PNG signature")
        handle.seek(-12, os.SEEK_END)  # a whole PNG ends with its IEND chunk
        if handle.read()[-8:-4] != b"IEND":
            sys.exit("entry.png is truncated: no IEND chunk at its tail")

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"

    before = page_digest(PAGE)
    publish(PAGE, target)
    if page_digest(target) != before:
        sys.exit("published copy failed its digest check")
    print(f"published {target} ({size} bytes, sha256 {before[:12]}…)")


if __name__ == "__main__":
    main()
