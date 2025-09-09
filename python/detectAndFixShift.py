"""
detectAndFixShift.py
====================

Detect and fix a single-byte shift in raw Bayer .bin images.

This module detects the most likely position of a missing byte (causing Bayer pattern break)
in a raw Bayer image and corrects the image by shifting the data and filling the lost byte with zero.
Useful for fixing corrupted satellite/camera Bayer images.

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
Execution:   python detectAndFixShift.py input.bin output_fixed.bin
"""

import numpy as np
import cv2

def detect_and_fix_shift(filename_in, filename_out, width=4096, height=4098, patch=8, stride=4096):
    # Load raw binary (8-bit Bayer RGGB)
    raw = np.fromfile(filename_in, dtype=np.uint8)
    expected_size = width * height
    if raw.size != expected_size:
        raise ValueError(f"File size {raw.size} does not match expected {expected_size}")

    raw_img = raw.reshape((height, width))

    # ---- Step 1: Detect missing byte anywhere in the frame ----
    scores = []
    positions = []

    for row in range(0, height - patch, patch):
        for col in range(0, width - patch, patch):
            crop = raw_img[row:row+patch, col:col+patch]
            rgb = cv2.cvtColor(crop.astype(np.uint8), cv2.COLOR_BAYER_RG2RGB)

            mean_r = rgb[:, :, 0].mean()
            mean_g = rgb[:, :, 1].mean()
            mean_b = rgb[:, :, 2].mean()
            score = mean_g / (mean_r + mean_b + 1e-6)

            scores.append(score)
            positions.append(row * width + col)  # global 1D index

    scores = np.array(scores)
    diffs = np.abs(np.diff(scores))

    # Position of biggest drop (where Bayer pattern broke)
    best_idx = positions[np.argmax(diffs)]
    print(f"Likely missing byte at global index {best_idx}, row={best_idx // width}, col={best_idx % width}")

    # ---- Step 2: Fix shift from that point onward ----
    raw_flat = raw.flatten()
    fixed = np.copy(raw_flat)

    fixed[best_idx+1:] = raw_flat[best_idx:-1]
    fixed[best_idx] = 0  # lost byte replaced with 0

    # Save corrected file
    fixed.tofile(filename_out)
    print(f"Corrected file written to {filename_out}")

# main function for testing
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Detect and fix Bayer shift in raw binary files.")
    parser.add_argument("input", help="Input raw binary file")
    parser.add_argument("output", help="Output corrected binary file")
    args = parser.parse_args()
    
    detect_and_fix_shift(args.input, args.output)