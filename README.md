

# BayerImageProcessor

**Author:** Ahmad Asyraf Ahmad Saibudin  
**Project developed as part of internship at [CSUG — Centre spatial universitaire de Grenoble](https://www.csug.fr)**

A comprehensive toolkit for processing raw Bayer images (`.bin` files) from satellite or camera sensors. This project provides both Python and C++ utilities for converting, analyzing, and correcting Bayer images, including batch processing, metadata extraction, and image shift correction.

## Project Structure

- `cpp/` — C++ source code and build files
	- `binToPng.cpp` — Main C++ tool for converting `.bin` Bayer images to PNG
	- `detectAndFixShift.cpp` — Detects and corrects image shifts in Bayer images
	- `shiftRightImage.c` — Utility for shifting images
	- `build/` — CMake/MSVC build outputs and binaries
- `python/` — Python scripts for Bayer image processing
	- `binToPng.py` — Main Python tool for conversion and metadata extraction
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
- **Graphical User Interface (GUI) features** (Python):
	- Select multiple files and/or directories for batch processing
	- Remove selected files/directories from the input list
	- Live progress bar and status label for feedback during processing
	- Series selection: process only a specific image series (auto-detected from filenames)
	- Compression level slider with live value label
	- Output mode, header/footer, and output directory selection
	- Prints the equivalent CLI command for the current GUI settings
	- Error and success popups for user feedback
	- Robust handling of edge cases (no input, no output, no files found, etc.)

## Requirements

### Python
- Python 3.x
- numpy
- opencv-python

Install Python dependencies:
```sh
pip install numpy opencv-python argparse ttkbootstrap
sudo apt-get install python3-tk  # For Debian/Ubuntu systems
```

### C++
- g++ (or MSVC)
- [OpenCV](https://opencv.org/) (if colorization or advanced image processing is needed)

## Usage

### Python

#### Command-Line Interface (CLI)

```sh
python python/binToPng.py [inputs] [options]
```

**Arguments:**
- `inputs` : One or more `.bin` files or directories containing `.bin` files
- `-o`, `--output` : Output directory (default: current directory)
- `-m`, `--mode` : Output mode (`normal`, `colorize`, `both`, `none`)
- `-c`, `--compression` : PNG compression level (0-9, default: 3)
- `-hf`, `--headerfooter` : Extract and write header/footer info to a text file

**Examples:**
- Convert a single file:
	```sh
	python python/binToPng.py test_images/03_20250715_162736_04_b.bin
	```
- Convert all `.bin` files in a folder, colorize only:
	```sh
	python python/binToPng.py test_images/ -m colorize
	```
- Extract header/footer info only (no PNG):
	```sh
	python python/binToPng.py test_images/03_20250715_162736_04_b.bin -m none -hf
	```
- Set maximum PNG compression:
	```sh
	python python/binToPng.py test_images/03_20250715_162736_04_b.bin -c 9
	```


#### Graphical User Interface (GUI)


The project includes a modern, multi-tool GUI for Bayer image processing, built with `tkinter` and `ttkbootstrap`. The GUI provides an intuitive, tabbed interface for all major features, including batch processing, metadata extraction, image correction, and shift detection/fixing.

**Launching the GUI:**

```sh
python python/BayerImageProcessor.py
```
or, if packaged:
```sh
dist/BayerImageProcessor.exe
```

**Main Features:**

- **Tabbed Interface:**
	- **Binary To PNG:** Convert `.bin` Bayer images to PNG (raw and/or colorized), extract header/footer metadata, batch process files/folders, and select image series.
	- **Shift Right Image:** Shift a region of a raw Bayer image buffer to the right by a specified number of bytes (for correcting misalignments).
	- **Detect & Fix Shift:** Detect and fix a single-byte shift in raw Bayer images (for repairing corrupted files).

- **Batch Processing:**
	Add multiple files and/or directories for batch conversion or correction. The GUI will recursively find all `.bin` files in selected folders.

- **Series Detection and Selection:**
	Automatically detects image series (e.g., `03_20250715_162736`) from filenames and allows you to process only a specific series, or all files at once.

- **Flexible Output Options:**
	- Choose output directory.
	- Select output mode: normal (raw PNG), colorized (RGB PNG), both, or metadata-only.
	- Adjust PNG compression level (0-9) with a live value label.
	- Optionally extract and save header/footer metadata for each image.

- **Shift Correction Tools:**
	- **Shift Right Image:** Specify shift count, start row/column, and (optionally) image width/height.
	- **Detect & Fix Shift:** Automatically detects the most likely position of a missing byte and corrects the image.

- **Live Feedback and Usability:**
	- Progress bar and status label for real-time feedback.
	- Error and success popups for user feedback.
	- Robust handling of edge cases (no input, no output, no files found, etc.).
	- All processing is threaded, so the GUI remains responsive during long operations.

- **Cross-platform:**
	Works on Windows, Linux, and macOS (with minor adjustments for icon format on non-Windows).

**Packaging the GUI as a Standalone Executable (Windows):**

You can package the GUI as a single-file Windows executable using PyInstaller. A batch script is provided:

```sh
cd python
packageBip.bat
```

This will:
- Clean previous build outputs.
- Create `dist/BayerImageProcessor.exe` (standalone, double-clickable).

**Note:**
- All GUI features are available regardless of whether you run from source or as a packaged executable.

### C++

Build with CMake or use provided MSVC solution in `cpp/build/`.

Run the C++ converter:
```sh
cpp\build\bin\Debug\binToPng.exe -o test_images\output\ test_images\03_20250715_162736_04_b_py.bin
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


## Documentation & Code Clarity

All main Python and C++ programs in this project now include detailed file/module docstrings or Doxygen-style headers at the top of each file. These headers provide:
- File/module purpose and summary
- Author and contributor information
- Creation and modification dates
- Versioning
- License and copyright
- Usage notes and requirements

This ensures the codebase is self-explanatory, easy to maintain, and ready for onboarding new contributors or future development.

## Summary

This project provides a robust, cross-language solution for Bayer image processing, including conversion, metadata extraction, error handling, shift correction, and comprehensive documentation. It is suitable for both research and production environments where reliability, flexibility, and maintainability are required.

---

© 2025 Ahmad Asyraf Ahmad Saibudin. Internship at CSUG (Centre spatial universitaire de Grenoble).
