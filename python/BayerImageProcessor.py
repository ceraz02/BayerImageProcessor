"""
BayerImageProcessor.py
======================

Convert raw Bayer .bin images (4098x4096) to PNG (raw and colorized), extract header/footer metadata, and batch process files/folders.

Features
--------
- Converts .bin files to PNG (raw and colorized)
- Batch processing of files/folders
- Extracts header/footer info (analog gain, integration time)
- Adjustable PNG compression
- Option to skip PNG and only extract metadata
- Series processing (process all files with a given prefix)

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
Requires numpy, opencv-python.
Execution:   python BayerImageProcessor.py [options] input1.bin input2.bin ... | folder1 folder2 ...
"""

import numpy as np
import cv2
import argparse
import os
import glob

# Helper for writing header/footer to the provided file
def write_header_footer_to_file(hf, bin_path, raw):
    base = os.path.splitext(os.path.basename(bin_path))[0]
    # Extract image number from base (assumes format regionID_timestamp_ImgNb)
    img_nb = base.split('_')[-1] if '_' in base else base
    header_bytes = raw[0, :11]
    footer_bytes = raw[-1, :66]
    hf.write(f"File: {img_nb}\n")
    hf.write(f"Header : {' '.join(f'{b:02X}' for b in header_bytes)}\n")
    hf.write(f"         {' '.join(str(b) for b in header_bytes)}\n")
    analog_gain = header_bytes[8]
    hf.write(f"Analog Gain : 0x{analog_gain:02X} ({analog_gain})\n")
    integration_time = int.from_bytes(header_bytes[9:11], byteorder='little')
    integration_time_ms = integration_time * 0.0104
    hf.write(f"Integration Time  : 0x{integration_time:04X} ({integration_time} = {integration_time_ms:.3f} ms)\n")
    hf.write(f"Footer : {' '.join(f'{b:02X}' for b in footer_bytes)}\n")
    hf.write(f"         {' '.join(str(b) for b in footer_bytes)}\n\n")

def process_bin_file(bin_path, output_dir, mode, compression_level, header_footer_path=None):
    with open(bin_path, "rb") as f:
        raw = np.fromfile(f, dtype=np.uint8)
    expected_size = 4098 * 4096
    if raw.size < expected_size:
        # Pad missing bytes with zeros
        raw = np.pad(raw, (0, expected_size - raw.size), 'constant')
    elif raw.size > expected_size:
        # Truncate extra bytes
        raw = raw[:expected_size]
    raw = raw.reshape((4098, 4096))
    raw_image = raw[1:4097, :]
    base = os.path.splitext(os.path.basename(bin_path))[0]
    compression_params = [cv2.IMWRITE_PNG_COMPRESSION, compression_level]
    if mode in ("normal", "both"):
        cv2.imwrite(os.path.join(output_dir, f"{base}.png"), raw_image, compression_params)
    if mode in ("colorize", "both"):
        rgb_image = cv2.cvtColor(raw_image, cv2.COLOR_BAYER_RG2RGB)
        cv2.imwrite(os.path.join(output_dir, f"{base}_colorize.png"), rgb_image, compression_params)
    # Header/Footer extraction and writing
    if header_footer_path:
        header_footer_file = os.path.join(output_dir, f"{base}_header_footer.txt")
        with open(header_footer_file, "w") as hf:
            write_header_footer_to_file(hf, bin_path, raw)

def process_series_bin_files(series_name, inputs, output_dir, mode, compression_level, write_headerfooter=False):
    pattern = f"{series_name}_*.bin"
    series_files = []
    for inp in inputs:
        if os.path.isdir(inp):
            series_files.extend(glob.glob(os.path.join(inp, pattern)))
        elif inp.lower().endswith(".bin") and os.path.basename(inp).startswith(f"{series_name}_"):
            series_files.append(inp)
    if not series_files:
        print("No matching .bin files found for the given series name.")
        return
    os.makedirs(output_dir, exist_ok=True)
    total_files = len(series_files)
    hf = None
    if write_headerfooter:
        header_footer_file = os.path.join(output_dir, f"{series_name}_header_footer.txt")
        hf = open(header_footer_file, "w")
    try:
        for idx, bin_file in enumerate(series_files, 1):
            print(f"Processing image {idx} of {total_files}: {os.path.basename(bin_file)}")
            with open(bin_file, "rb") as f:
                raw = np.fromfile(f, dtype=np.uint8)
            expected_size = 4098 * 4096
            if raw.size < expected_size:
                raw = np.pad(raw, (0, expected_size - raw.size), 'constant')
            elif raw.size > expected_size:
                raw = raw[:expected_size]
            raw = raw.reshape((4098, 4096))
            # Optionally write header/footer info for this file
            if hf:
                write_header_footer_to_file(hf, bin_file, raw)
            # Optionally, generate PNGs if requested
            base = os.path.splitext(os.path.basename(bin_file))[0]
            compression_params = [cv2.IMWRITE_PNG_COMPRESSION, compression_level]
            raw_image = raw[1:4097, :]
            if mode in ("normal", "both"):
                cv2.imwrite(os.path.join(output_dir, f"{base}.png"), raw_image, compression_params)
            if mode in ("colorize", "both"):
                rgb_image = cv2.cvtColor(raw_image, cv2.COLOR_BAYER_RG2RGB)
                cv2.imwrite(os.path.join(output_dir, f"{base}_colorize.png"), rgb_image, compression_params)
    finally:
        if hf:
            hf.close()

parser = argparse.ArgumentParser(description="Convert binary Bayer images to PNG.")
parser.add_argument("inputs", nargs="+", help="Input .bin files or directories")
parser.add_argument("-o", "--output", default=".", help="Output directory. Default is current directory.")
parser.add_argument(
    "-m", "--mode",
    choices=["normal", "colorize", "both", "none"],
    default="colorize",
    help="Output mode: normal (raw PNG), colorize (RGB PNG), both, or none (no PNG output, only header/footer if requested). Default is colorize."
)
parser.add_argument(
    "-c", "--compression", type=int, default=3, choices=range(0,10), metavar="[0-9]",
    help="PNG compression level: 0 (none, fastest) to 9 (max, slowest). Default is 3."
)
parser.add_argument(
    "-hf", "--headerfooter", action="store_true", help="Extract and write header/footer info to a text file."
)
parser.add_argument(
    "-s", "--series", type=str, help="Series name for image series processing (e.g. 03_20250715_162736)")

args = parser.parse_args()

if args.series:
    process_series_bin_files(
        args.series, args.inputs, args.output, args.mode, args.compression,
        write_headerfooter=args.headerfooter
    )
else:
    # Gather all .bin files from inputs
    bin_files = []
    for inp in args.inputs:
        if os.path.isdir(inp):
            bin_files.extend(glob.glob(os.path.join(inp, "*.bin")))
        elif inp.lower().endswith(".bin"):
            bin_files.append(inp)
    if not bin_files:
        print("No .bin files found.")
        exit(1)
    os.makedirs(args.output, exist_ok=True)
    total_files = len(bin_files)
    for idx, bin_file in enumerate(bin_files, 1):
        print(f"Processing image {idx} of {total_files}: {os.path.basename(bin_file)}")
        process_bin_file(
            bin_file, args.output, args.mode, args.compression,
            header_footer_path=args.headerfooter if args.headerfooter else None
        )
