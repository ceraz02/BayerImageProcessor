

# BayerImageProcessor

**Author:** Ahmad Asyraf Ahmad Saibudin  
**Project developed as part of internship at [CSUG — Centre spatial universitaire de Grenoble](https://www.csug.fr)**

A comprehensive toolkit for processing raw Bayer images (`.bin` files) from satellite or camera sensors. This project provides both Python and C++ utilities for converting, analyzing, and correcting Bayer images, including batch processing, metadata extraction, and image shift correction.

## Project Structure

- `cpp/` — C++ source code and build files
	- `BayerImageProcessor.cpp` — Main C++ tool for converting `.bin` Bayer images to PNG
	- `detectAndFixShift.cpp` — Detects and corrects image shifts in Bayer images
	- `shiftRightImage.c` — Utility for shifting images
	- `build/` — CMake/MSVC build outputs and binaries
- `python/` — Python scripts for Bayer image processing
	- `BayerImageProcessor.py` — Main Python tool for conversion and metadata extraction
	- `detectAndFixShift.py`, `shiftRightImage.py`, `diffBinImage.py` — Additional utilities for shift correction and comparison
- `test_images/` — Sample `.bin` images and expected outputs for testing
- `output/` — Output directory for generated PNGs and metadata

## Features

- **Convert raw Bayer `.bin` files (4098x4096) to PNG** (raw and colorized)
- **Batch processing**: Process multiple files or entire folders
- **Header/Footer extraction**: Extracts header (first 11 bytes) and footer (first 66 bytes) metadata, including analog gain and integration time
- **Corrupted file handling**: Pads incomplete files with zeros for robust conversion
- **Image shift detection and correction**: Tools to detect and fix horizontal/vertical shifts in images (Python and C++)
- **Adjustable PNG compression** (Python)
- **Flexible output modes**: Choose between normal, colorized, both, or metadata-only outputs
- **Cross-language parity**: Both Python and C++ tools provide similar functionality for comparison and validation

## Requirements

### Python
- Python 3.x
- numpy
- opencv-python

Install Python dependencies:
```sh
pip install numpy opencv-python
```

### C++
- g++ (or MSVC)
- [OpenCV](https://opencv.org/) (if colorization or advanced image processing is needed)

## Usage

### Python

```sh
python python/BayerImageProcessor.py [inputs] [options]
```

#### Arguments
- `inputs` : One or more `.bin` files or directories containing `.bin` files
- `-o`, `--output` : Output directory (default: current directory)
- `-m`, `--mode` : Output mode (`normal`, `colorize`, `both`, `none`)
- `-c`, `--compression` : PNG compression level (0-9, default: 3)
- `-hf`, `--headerfooter` : Extract and write header/footer info to a text file

#### Examples
- Convert a single file:
	```sh
	python python/BayerImageProcessor.py test_images/03_20250715_162736_04_b.bin
	```
- Convert all `.bin` files in a folder, colorize only:
	```sh
	python python/BayerImageProcessor.py test_images/ -m colorize
	```
- Extract header/footer info only (no PNG):
	```sh
	python python/BayerImageProcessor.py test_images/03_20250715_162736_04_b.bin -m none -hf
	```
- Set maximum PNG compression:
	```sh
	python python/BayerImageProcessor.py test_images/03_20250715_162736_04_b.bin -c 9
	```

### C++

Build with CMake or use provided MSVC solution in `cpp/build/`.

Run the C++ processor:
```sh
cpp\build\bin\Debug\BayerImageProcessor.exe -o test_images\output\ test_images\03_20250715_162736_04_b_py.bin
```

Run shift detection/correction:
```sh
cpp\build\bin\Debug\detectAndFixShift.exe input.bin reference.bin
```

### Additional Utilities

- `python/detectAndFixShift.py` — Python version of shift detection/correction
- `python/shiftRightImage.py` — Shift image rows/columns
- `python/diffBinImage.py` — Compare two `.bin` images

## Output

- PNG images: `image.png`, `image_colorize.png`
- Header/footer info: `image_header_footer.txt`
- Corrected/shifted images: output to specified directory

## File Naming Conventions

- Output files are named based on the input, with suffixes for colorized or processed versions (e.g., `_colorize.png`, `_header_footer.txt`)

## Testing

- Use files in `test_images/` to validate processing and compare outputs between Python and C++ implementations.

## Summary

This project provides a robust, cross-language solution for Bayer image processing, including conversion, metadata extraction, error handling, and shift correction. It is suitable for both research and production environments where reliability and flexibility are required.

---

© 2025 Ahmad Asyraf Ahmad Saibudin. Internship at CSUG (Centre spatial universitaire de Grenoble).
