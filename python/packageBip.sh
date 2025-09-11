#!/bin/bash
# Change to script directory
cd "$(dirname "$0")"

# Clean previous build/dist if exist
rm -rf build dist
[ -f BayerImageProcessor.spec ] && rm BayerImageProcessor.spec

# Build the GUI app with PNG icon for Linux/macOS
pyinstaller \
    BayerImageProcessor.py \
    --noconfirm \
    --onefile \
    --icon="../assets/bip-icon.png" \
    --name "BayerImageProcessor" \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=PIL.ImageTk \
    --add-data "../assets/bip-icon.png:assets"
# --windowed

# Check if build succeeded
if [ -f dist/BayerImageProcessor ]; then
    echo "Build succeeded! Find your executable in dist/BayerImageProcessor"
else
    echo "Build failed. Check the output above for errors."
fi
