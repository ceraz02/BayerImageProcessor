import numpy as np
import cv2
import argparse
import os
import glob

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
        header_bytes = raw[0, :11]
        footer_bytes = raw[-1, :66]
        with open(os.path.join(output_dir, f"{base}_header_footer.txt"), "w") as hf:
            # Header
            hf.write(f"Header : {' '.join(f'{b:02X}' for b in header_bytes)}\n")
            hf.write(f"         {' '.join(str(b) for b in header_bytes)}\n")
            # Analog Gain (byte 8)
            analog_gain = header_bytes[8]
            hf.write(f"Analog Gain : 0x{analog_gain:02X} ({analog_gain})\n")
            # Integration Time (bytes 9 and 10, little-endian)
            integration_time = int.from_bytes(header_bytes[9:11], byteorder='little')
            integration_time_ms = integration_time * 0.0104
            hf.write(f"Integration Time  : 0x{integration_time:04X} ({integration_time} = {integration_time_ms:.3f} ms)\n")
            # Footer
            hf.write(f"Footer : {' '.join(f'{b:02X}' for b in footer_bytes)}\n")
            hf.write(f"         {' '.join(str(b) for b in footer_bytes)}\n")

parser = argparse.ArgumentParser(description="Convert binary Bayer images to PNG.")
parser.add_argument("inputs", nargs="+", help="Input .bin files or directories")
parser.add_argument("-o", "--output", default=".", help="Output directory")
parser.add_argument(
    "-m", "--mode",
    choices=["normal", "colorize", "both", "none"],
    default="both",
    help="Output mode: normal (raw PNG), colorize (RGB PNG), both, or none (no PNG output, only header/footer if requested)"
)
parser.add_argument(
    "-c", "--compression", type=int, default=3, choices=range(0,10), metavar="[0-9]",
    help="PNG compression level: 0 (none, fastest) to 9 (max, slowest). Default is 3."
)
parser.add_argument(
    "-hf", "--headerfooter", action="store_true", help="Extract and write header/footer info to a text file."
)
args = parser.parse_args()

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

for bin_file in bin_files:
    process_bin_file(
        bin_file, args.output, args.mode, args.compression,
        header_footer_path=args.headerfooter if args.headerfooter else None
    )
