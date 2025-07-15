# binToPng

A Python tool to convert binary Bayer images (.bin) to PNG format, extract header/footer metadata, and handle corrupted files gracefully.

## Features
- Converts raw Bayer .bin files (4098x4096) to PNG (raw and colorized)
- Supports batch processing of multiple files or folders
- Extracts header (first 11 bytes) and footer (first 66 bytes) metadata
- Parses analog gain and integration time (with ms conversion)
- Handles corrupted/incomplete files by padding missing bytes with zeros
- Adjustable PNG compression level
- Option to skip PNG generation and only extract metadata

## Requirements
- Python 3.x
- numpy
- opencv-python

Install dependencies:
```sh
pip install numpy opencv-python
```

## Usage
```sh
python3 main.py [inputs] [options]
```

### Arguments
- `inputs` : One or more .bin files or directories containing .bin files
- `-o`, `--output` : Output directory (default: current directory)
- `-m`, `--mode` : Output mode (`normal`, `colorize`, `both`, `none`)
- `-c`, `--compression` : PNG compression level (0-9, default: 3)
- `-hf`, `--headerfooter` : Extract and write header/footer info to a text file

### Examples
Convert a single file:
```sh
python3 main.py image.bin
```

Convert all .bin files in a folder, colorize only:
```sh
python3 main.py /path/to/folder -m colorize
```

Extract header/footer info only (no PNG):
```sh
python3 main.py image.bin -m none -hf
```

Set maximum PNG compression:
```sh
python3 main.py image.bin -c 9
```

## Output
- PNG images: `image.png`, `image_colorize.png`
- Header/footer info: `image_header_footer.txt`
