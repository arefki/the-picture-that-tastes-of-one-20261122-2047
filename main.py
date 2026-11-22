#!/usr/bin/env python3
"""Entrypoint for 'Golden Honey Drip' (make.fun program/v1).

Copies the pre-rendered entry image to /output/entry.png so the grader
can collect it. Pure standard library, deterministic, no network.

The output is verified before the program exits (PNG signature, 1024x1024,
at most 1,048,576 bytes) and left world-readable (mode 0644): the grader
collects outputs as another user, so a 0600 file would fail as unreadable.
"""
import os
import shutil
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST_DIR = "/output"
DST = os.path.join(DST_DIR, "entry.png")

MAX_BYTES = 1_048_576
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def check_png(path):
    """Assert the file is a 1024x1024 PNG within the size limit."""
    size = os.path.getsize(path)
    assert size <= MAX_BYTES, "entry.png too large: %d bytes" % size
    with open(path, "rb") as f:
        header = f.read(33)
    assert header[:8] == PNG_SIGNATURE, "entry.png is not a PNG"
    # IHDR: width and height are the first two big-endian uint32s after
    # the 8-byte signature and the 4-byte length + 4-byte chunk type.
    width, height = struct.unpack(">II", header[16:24])
    assert (width, height) == (1024, 1024), "bad dimensions: %dx%d" % (
        width,
        height,
    )


def main():
    os.makedirs(DST_DIR, exist_ok=True)
    shutil.copyfile(SRC, DST)
    check_png(DST)
    os.chmod(DST, 0o644)


if __name__ == "__main__":
    main()
