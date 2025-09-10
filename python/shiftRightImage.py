"""
shiftRightImage.py
==================

Shift a region of a raw Bayer .bin image buffer to the right by a specified number of bytes.

This module is used to correct misalignments in binary image data. Mimics the behavior of the C version (shiftRightImage.c).

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
Execution:   python shiftRightImage.py img_file shift_count start_row [start_col [img_width img_height]]
"""

import sys
import os
import numpy as np

IMG_WIDTH = 4096
FRAME_HEIGHT = 4098


def shift_image_region_numpy(buf: np.ndarray, img_width: int, img_height: int,
                             shift_count: int, start_row: int, start_col: int) -> int:
    if shift_count < 1:
        print(f"ERROR in shiftImageRegion: Invalid shift_count {shift_count}. Must be >= 1.")
        return 1

    if start_row < 0 or start_row >= img_height or start_col < 0 or start_col >= img_width:
        print(f"ERROR in shiftImageRegion: Invalid start_row/start_col ({start_row},{start_col}).")
        return 1

    # Reshape flat buffer into 2D image
    img = buf.reshape((img_height, img_width))

    # Flattened offset (like in C)
    offset = start_row * img_width + start_col
    total_pixels = img_width * img_height
    if offset < 0 or offset >= total_pixels:
        print(f"ERROR in shiftImageRegion: Invalid offset ({offset}).")
        return 1

    region_size = total_pixels - offset
    if shift_count < 1 or shift_count > region_size:
        print(f"ERROR in shiftImageRegion: Invalid shift_count {shift_count} for region size {region_size}.")
        return 1

    # Flatten again from offset onwards and shift
    region = img.ravel()[offset:]
    region[shift_count:] = region[:-shift_count]
    region[:shift_count] = 0

    return 0


def shift_right_image_file(img_file, shift_count, start_row, start_col=0, img_width=4096, img_height=4098):
    if shift_count < 1:
        print(f"ERROR in shiftRightImage: Invalid shift_count {shift_count}. Must be >= 1.")
        return 1

    if start_row < 0 or start_row >= img_height or start_col < 0 or start_col >= img_width:
        print(f"ERROR in shiftRightImage: Invalid start_row/start_col ({start_row},{start_col}).")
        return 1

    try:
        fsize = os.path.getsize(img_file)
    except OSError as e:
        print(f"ERROR in shiftRightImage: Could not open file {img_file} - {e}")
        return 1

    if fsize != img_width * img_height:
        print(f"ERROR in shiftRightImage: Incorrect file size for {img_file}: {fsize} != expected {img_width * img_height}")
        return 1

    try:
        with open(img_file, "rb+") as fd:
            buf = np.frombuffer(fd.read(), dtype=np.uint8).copy()
            if buf.size != img_width * img_height:
                print(f"ERROR in shiftRightImage: Incomplete read. Got {buf.size} pixels instead of {img_width * img_height}")
                return 1

            result = shift_image_region_numpy(buf, img_width, img_height, shift_count, start_row, start_col)
            if result != 0:
                print(f"ERROR in shiftRightImage: shiftImageRegion failed with error code {result}")
                return result

            fd.seek(0)
            fd.write(buf.tobytes())
            fd.flush()

    except Exception as e:
        print(f"ERROR in shiftRightImage: Exception occurred - {e}")
        return 1

    print(f"Successfully shifted image region in {img_file}")
    return 0

def main():

    argc = len(sys.argv)
    if argc not in (4, 5, 7):
        print(f"USAGE: {sys.argv[0]} img_file shift_count start_row [start_col [img_width img_height]]")
        return 1

    img_file = sys.argv[1]
    shift_count = int(sys.argv[2])
    start_row = int(sys.argv[3])
    start_col = int(sys.argv[4]) if argc >= 5 else 0
    img_width = int(sys.argv[5]) if argc == 7 else IMG_WIDTH
    img_height = int(sys.argv[6]) if argc == 7 else FRAME_HEIGHT

    return shift_right_image_file(img_file, shift_count, start_row, start_col, img_width, img_height)


if __name__ == "__main__":
    sys.exit(main())
