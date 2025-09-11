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
- CLI and GUI (Tkinter/ttkbootstrap) modes

Authors
-------
- Ahmad Asyraf Ahmad Saibudin (original author)

Created: 2025-07-16
Last modified: 2025-09
Version: 1.1

License
-------
CSUG 2022-2025. All rights reserved.

Notes
-----
Requires numpy, opencv-python, and ttkbootstrap.

Usage (CLI)
-----------
    python BayerImageProcessor.py input1.bin input2.bin -o output_dir -m colorize -c 3 -hf -s SERIES

Usage (GUI)
-----------
    python BayerImageProcessor.py
    # Use the graphical interface to select files, options, and process
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import numpy as np
import cv2
import glob
import argparse


# Helper for writing header/footer to the provided file
def write_header_footer_to_file(hf, bin_path, raw):
    base = os.path.splitext(os.path.basename(bin_path))[0]
    # Extract image number from base (assumes format regionID_timestamp_ImgNb)
    parts = base.split('_', 3)
    if len(parts) >= 4:
        img_nb = parts[3]
    else:
        img_nb = base
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

def process_bin_file(bin_path, output_dir, mode, compression_level, headerfooter=False):
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
    if headerfooter:
        header_footer_file = os.path.join(output_dir, f"{base}_header_footer.txt")
        with open(header_footer_file, "w") as hf:
            write_header_footer_to_file(hf, bin_path, raw)

def process_series_bin_files(series_name, inputs, output_dir, mode, compression_level, write_headerfooter=False, progress_callback=None):
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
            if progress_callback:
                progress_callback(idx, total_files, bin_file)
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
    
# Unified entry point for GUI and CLI
def process_bayer_images(inputs, output, mode, compression, headerfooter, series=None, progress_callback=None):
    if series:
        process_series_bin_files(series, inputs, output, mode, compression, write_headerfooter=headerfooter, progress_callback=progress_callback)
    else:
        # Gather all .bin files from inputs
        bin_files = []
        for inp in inputs:
            if os.path.isdir(inp):
                bin_files.extend(glob.glob(os.path.join(inp, "*.bin")))
            elif inp.lower().endswith(".bin"):
                bin_files.append(inp)
        if not bin_files:
            print("No .bin files found in the provided inputs.")
            return
        os.makedirs(output, exist_ok=True)
        total = len(bin_files)
        for idx, bin_file in enumerate(bin_files, 1):
            if progress_callback:
                progress_callback(idx, total, bin_file)
            process_bin_file(bin_file, output, mode, compression, headerfooter)


# CLI logic
def cli_main(args=None):
    parser = argparse.ArgumentParser(description="Convert raw Bayer .bin images (4098x4096) to PNG (raw and colorized), extract header/footer metadata, and batch process files/folders. (If arguments are provided, runs in CLI mode; otherwise, launches GUI.)")
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

    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    process_bayer_images(args.inputs, args.output, args.mode, args.compression, args.headerfooter, args.series)



# Tkinter GUI setup

import threading
# from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap import Style

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Image Processor")
        self.style = ttk.Style("flatly")
        self.input_paths = []
        self.output_dir = ""
        self.series_options = []
        self.selected_series = tk.StringVar()
        self.root.resizable(True, False)
        self.root.minsize(510, 500)


        # Input and series selection frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=(10, 0), fill=tk.X)
        self.input_label = tk.Label(input_frame, text="Input files or directories:")
        self.input_label.pack()
        listbox_frame = tk.Frame(input_frame)
        listbox_frame.pack(pady=2, fill=tk.X)
        self.input_listbox = tk.Listbox(listbox_frame, width=60, height=5, selectmode=tk.EXTENDED)
        self.input_listbox.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=self.input_listbox.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.input_listbox.config(yscrollcommand=scrollbar.set)
        btn_frame = tk.Frame(input_frame)
        btn_frame.pack(pady=2)
        self.input_file_btn = tk.Button(btn_frame, text="Add Files", command=self.add_files)
        self.input_file_btn.pack(side=tk.LEFT, padx=2)
        self.input_dir_btn = tk.Button(btn_frame, text="Add Directory", command=self.add_directory)
        self.input_dir_btn.pack(side=tk.LEFT, padx=2)
        self.remove_btn = tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected)
        self.remove_btn.pack(side=tk.LEFT, padx=2)

        # Series selection (initially hidden, but in input_frame)
        self.series_label = tk.Label(input_frame, text="Select series to process (optional):")
        self.series_combobox = ttk.Combobox(input_frame, textvariable=self.selected_series, state="readonly", width=40)
        self.series_label.pack_forget()
        self.series_combobox.pack_forget()

        # Output directory selection
        self.output_label = tk.Label(root, text="Output directory:")
        self.output_label.pack(pady=(10, 0))
        out_frame = tk.Frame(root)
        out_frame.pack(pady=2)
        self.output_entry = tk.Entry(out_frame, width=50)
        self.output_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.output_button = tk.Button(out_frame, text="Browse", command=self.browse_output_dir)
        self.output_button.pack(side=tk.LEFT)

        # Mode selection (normal, colorize, both, none)
        self.mode_label = tk.Label(root, text="Output mode:")
        self.mode_label.pack(pady=(10, 0))
        mode_frame = tk.Frame(root)
        mode_frame.pack()
        self.mode_var = tk.StringVar(value="colorize")
        self.mode_normal = tk.Radiobutton(mode_frame, text="Normal", variable=self.mode_var, value="normal")
        self.mode_normal.pack(side=tk.LEFT, padx=2)
        self.mode_colorize = tk.Radiobutton(mode_frame, text="Colorize", variable=self.mode_var, value="colorize")
        self.mode_colorize.pack(side=tk.LEFT, padx=2)
        self.mode_both = tk.Radiobutton(mode_frame, text="Both", variable=self.mode_var, value="both")
        self.mode_both.pack(side=tk.LEFT, padx=2)
        self.mode_none = tk.Radiobutton(mode_frame, text="None", variable=self.mode_var, value="none")
        self.mode_none.pack(side=tk.LEFT, padx=2)

        # Compression level
        self.compression_label = tk.Label(root, text="Compression level (0-9):")
        self.compression_label.pack(pady=(10, 0))
        compression_frame = tk.Frame(self.root)
        compression_frame.pack(pady=2)
        self.compression_scale = tk.Scale(compression_frame, from_=0, to=9, orient="horizontal", length=200, showvalue=0, command=self.update_compression_value)
        self.compression_scale.set(3)
        self.compression_scale.pack(side=tk.LEFT)
        self.compression_value_label = tk.Label(compression_frame, text=str(self.compression_scale.get()))
        self.compression_value_label.pack(side=tk.LEFT, padx=(8,0))

        # Header/Footer checkbox
        self.header_footer_var = tk.BooleanVar()
        self.header_footer_checkbox = tk.Checkbutton(root, text="Save header/footer info", variable=self.header_footer_var)
        self.header_footer_checkbox.pack(pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=(10, 2))

        # Status label
        self.status_label = tk.Label(root, text="Ready", fg="blue")
        self.status_label.pack(pady=(0, 5))

        # Start button
        self.start_button = tk.Button(root, text="Start Processing", command=self.start_processing)
        self.start_button.pack(pady=10)

    def update_compression_value(self, val):
        self.compression_value_label.config(text=str(val))
    
    def add_files(self):
        files = filedialog.askopenfilenames(title="Select .bin files", filetypes=[("Binary files", "*.bin")])
        for f in files:
            if f not in self.input_paths:
                self.input_paths.append(f)
                self.input_listbox.insert(tk.END, f)
        self.analyze_series()

    def add_directory(self):
        d = filedialog.askdirectory(title="Select directory with .bin files")
        if d and d not in self.input_paths:
            self.input_paths.append(d)
            self.input_listbox.insert(tk.END, d)
        self.analyze_series()

    def remove_selected(self):
        selected = list(self.input_listbox.curselection())
        for idx in reversed(selected):
            self.input_listbox.delete(idx)
            del self.input_paths[idx]
        self.analyze_series()

    def analyze_series(self):
        # Scan all .bin files in input_paths and extract series prefixes
        import re
        filelist = []
        for path in self.input_paths:
            if os.path.isdir(path):
                filelist.extend([os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.bin')])
            else:
                filelist.append(path)
        # Extract series prefix (e.g., 03_20250715_162736 from 03_20250715_162736_04.bin)
        series_set = set()
        pattern = re.compile(r"^([\w]+_\d{8}_\d{6})_")
        for f in filelist:
            base = os.path.basename(f)
            m = pattern.match(base)
            if m:
                series_set.add(m.group(1))
        self.series_options = sorted(series_set)
        if self.series_options:
            self.series_label.pack(pady=(10, 0))
            self.series_combobox['values'] = ["(All)"] + self.series_options
            self.series_combobox.current(0)
            self.series_combobox.pack()
        else:
            self.series_label.pack_forget()
            self.series_combobox.pack_forget()
        self.selected_series.set("")

    def browse_output_dir(self):
        d = filedialog.askdirectory(title="Select output directory")
        if d:
            self.output_dir = d
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, d)

    def set_status(self, msg, color="blue"):
        self.status_label.config(text=msg, fg=color)

    def start_processing(self):
        if not self.input_paths or not self.output_entry.get():
            messagebox.showerror("Error", "Please select input files/directories and output directory.")
            return
        self.output_dir = self.output_entry.get()
        # Print equivalent CLI arguments
        cli_args = ["python BayerImageProcessor.py"]
        # Inputs
        for inp in self.input_paths:
            cli_args.append(f'"{inp}"')
        # Output
        cli_args.append(f'-o "{self.output_dir}"')
        # Mode
        mode = self.mode_var.get()
        if mode:
            cli_args.append(f'-m {mode}')
        # Compression
        compression = self.compression_scale.get()
        if compression != 3:
            cli_args.append(f'-c {compression}')
        # Header/footer
        if self.header_footer_var.get():
            cli_args.append('-hf')
        # Series
        selected_series = self.series_combobox.get() if self.series_options else ""
        if selected_series and selected_series != "(All)":
            cli_args.append(f'-s {selected_series}')
        print("[GUI->CLI] Equivalent command:")
        print(" ".join(cli_args))

        self.start_button.config(state=tk.DISABLED)
        self.set_status("Processing...", color="orange")
        self.progress['value'] = 0
        self.root.update_idletasks()
        thread = threading.Thread(target=self.process_all)
        thread.start()

    def process_all(self):
        mode = self.mode_var.get()
        compression_level = self.compression_scale.get()
        write_headerfooter = self.header_footer_var.get()
        import re
        filelist = []
        for path in self.input_paths:
            if os.path.isdir(path):
                filelist.extend([os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.bin')])
            else:
                filelist.append(path)
        # If a series is selected, filter filelist
        selected_series = self.series_combobox.get() if self.series_options else ""
        if selected_series and selected_series != "(All)":
            # Use series string directly (no re.escape) so underscores are not escaped
            pattern = re.compile(rf"^{selected_series}_\d+\.bin$")
            # debug_checked = []
            filtered = []
            for f in filelist:
                fname = os.path.basename(f)
                # debug_checked.append(fname)
                if pattern.match(fname):
                    filtered.append(f)
            # print(f"[DEBUG] Files checked for series '{selected_series}': {debug_checked}")
            # print(f"[DEBUG] Files matched for series '{selected_series}': {[os.path.basename(f) for f in filtered]}")
            if not filtered:
                self.set_status(f"No .bin files found for series {selected_series}.", color="red")
                self.start_button.config(state=tk.NORMAL)
                return
            # Use process_series_bin_files for series
            self.progress['maximum'] = len(filtered)
            errors = []
            try:
                process_series_bin_files(selected_series, self.input_paths, self.output_dir, mode, compression_level, write_headerfooter)
            except Exception as e:
                errors.append(str(e))
            self.progress['value'] = len(filtered)
            self.set_status(f"Processing complete for series {selected_series}.", color="green" if not errors else "red")
            self.start_button.config(state=tk.NORMAL)
            if errors:
                messagebox.showwarning("Done with errors", "Some files failed to process:\n" + "\n".join(errors))
            else:
                messagebox.showinfo("Success", f"Processing complete for series {selected_series}!")
            return
        # Otherwise, process all files as before
        total = len(filelist)
        if total == 0:
            self.set_status("No .bin files found.", color="red")
            self.start_button.config(state=tk.NORMAL)
            return
        self.progress['maximum'] = total
        errors = []
        for idx, bin_path in enumerate(filelist, 1):
            try:
                process_bin_file(bin_path, self.output_dir, mode, compression_level, write_headerfooter)
            except Exception as e:
                errors.append(f"{os.path.basename(bin_path)}: {e}")
            self.progress['value'] = idx
            self.set_status(f"Processing {idx}/{total}: {os.path.basename(bin_path)}")
            self.root.update_idletasks()
        self.start_button.config(state=tk.NORMAL)
        if errors:
            self.set_status(f"Done with {len(errors)} errors.", color="red")
            messagebox.showwarning("Done with errors", "Some files failed to process:\n" + "\n".join(errors))
        else:
            self.set_status("Processing complete!", color="green")
            messagebox.showinfo("Success", "Processing complete!")

# Run the app
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cli_main()
    else:
        root = tk.Tk()
        app = ImageProcessorApp(root)
        root.mainloop()
