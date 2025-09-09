"""
diffBinImage.py
===============

Compare two binary image files byte-by-byte and report differing regions.

This module compares two binary image files and reports the regions where they differ.

Authors
-------
- Ahmad Asyraf Ahmad Saibudin (original author)

Created: 2025-07-16
Last modified: 2025-09
Version: 1.0

License
-------
CSUG 2022-2025. All rights reserved.

Notes
-----
Execution:   python diffBinImage.py file1.bin file2.bin
"""

import sys

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} file1 file2")
    sys.exit(1)

file1 = sys.argv[1]
file2 = sys.argv[2]

with open(file1, "rb") as f1, open(file2, "rb") as f2:
    pos = 0
    diff_start = None

    while True:
        b1 = f1.read(1)
        b2 = f2.read(1)

        if not b1 and not b2:
            if diff_start is not None:
                print(f"Difference from byte {diff_start} to {pos - 1}")
            break

        if b1 != b2:
            if diff_start is None:
                diff_start = pos
        else:
            if diff_start is not None:
                print(f"Difference from byte {diff_start} to {pos - 1}")
                diff_start = None

        pos += 1

    # If one file is longer than the other
    extra1 = f1.read()
    extra2 = f2.read()
    if extra1:
        print(f"{file1} is longer starting at byte {pos}")
    elif extra2:
        print(f"{file2} is longer starting at byte {pos}")
