
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
from tkinter import ttk

# Import main functions from the three scripts
from BayerImageProcessor import process_bayer_images
from shiftRightImage import shift_right_image_file
from detectAndFixShift import detect_and_fix_shift

class BayerImageProcessorTab(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		self.input_paths = []
		self.output_dir = ""
		self.selected_series = tk.StringVar()
		self.series_options = []
		self.create_widgets()

	def create_widgets(self):
		# Input files
		input_frame = tk.LabelFrame(self, text="Input .bin files or directories")
		input_frame.pack(fill=tk.X, padx=10, pady=5)
		listbox_frame = tk.Frame(input_frame)
		listbox_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
		self.input_listbox = tk.Listbox(listbox_frame, width=60, height=4, selectmode=tk.EXTENDED)
		self.input_listbox.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
		scrl = tk.Scrollbar(listbox_frame, command=self.input_listbox.yview)
		scrl.pack(side=tk.RIGHT, fill=tk.Y)
		self.input_listbox.config(yscrollcommand=scrl.set)
		btn_frame = tk.Frame(input_frame)
		btn_frame.pack(side=tk.LEFT, padx=5)
		tk.Button(btn_frame, text="Add Files", command=self.add_files).pack(fill=tk.X, pady=2)
		tk.Button(btn_frame, text="Add Directory", command=self.add_directory).pack(fill=tk.X, pady=2)
		tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(fill=tk.X, pady=2)

		# Series name
		series_frame = tk.LabelFrame(self, text="Series name (optional)")
		series_frame.pack(fill=tk.X, padx=10, pady=5)
		# self.series_entry = tk.Entry(series_frame, width=30)
		# self.series_entry.pack(side=tk.LEFT, padx=5, pady=5)
		self.series_entry = ttk.Combobox(series_frame, textvariable=self.selected_series, state="readonly", width=40)
		self.series_entry.pack(side=tk.LEFT, padx=5, pady=5)

		# Output directory
		out_frame = tk.LabelFrame(self, text="Output directory")
		out_frame.pack(fill=tk.X, padx=10, pady=5)
		self.output_entry = tk.Entry(out_frame, width=50)
		self.output_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
		tk.Button(out_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.LEFT, padx=5)

		# Mode
		mode_frame = tk.LabelFrame(self, text="Output mode")
		mode_frame.pack(fill=tk.X, padx=10, pady=5)
		self.mode_var = tk.StringVar(value="colorize")
		for text, val in [("Normal", "normal"), ("Colorize", "colorize"), ("Both", "both"), ("None", "none")]:
			tk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=val).pack(side=tk.LEFT, padx=5)

		# Compression
		comp_frame = tk.LabelFrame(self, text="Compression level (0-9)")
		comp_frame.pack(fill=tk.X, padx=10, pady=5)
		self.compression_scale = tk.Scale(comp_frame, from_=0, to=9, orient="horizontal", length=200, showvalue=0, command=self.update_compression_value)
		self.compression_scale.set(3)
		self.compression_scale.pack(side=tk.LEFT, padx=5)
		self.compression_value_label = tk.Label(comp_frame, text="3")
		self.compression_value_label.pack(side=tk.LEFT, padx=5)

		# Header/Footer
		self.header_footer_var = tk.BooleanVar()
		tk.Checkbutton(self, text="Save header/footer info", variable=self.header_footer_var).pack(pady=5)

		# Progress and status
		self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
		self.progress.pack(pady=5)
		self.status_label = tk.Label(self, text="Ready", fg="blue")
		self.status_label.pack(pady=2)

		# Start button
		self.start_button = tk.Button(self, text="Start Processing", command=self.start_processing)
		self.start_button.pack(pady=10)
  
	def update_compression_value(self, val):
		self.compression_value_label.config(text=str(val))
  
	def analyze_series(self):
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
			self.series_entry['values'] = ["(All)"] + self.series_options
			self.series_entry.current(0)
			self.series_entry.config(state="readonly")
		else:
			self.series_entry.set("")
			self.series_entry['values'] = []
			self.series_entry.config(state="disabled")
		self.selected_series.set("")

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
			self.set_status("Please select input(s) and output directory", color="red")
			return
		self.start_button.config(state=tk.DISABLED)
		self.set_status("Processing...", color="orange")
		self.progress['value'] = 0
		self.update_idletasks()
		thread = threading.Thread(target=self.process_all)
		thread.start()

	def process_all(self):
		# Gather parameters
		self.output_dir = self.output_entry.get()
		series_name = self.selected_series.get()
		if series_name == "(All)":
			series_name = None
		try:
			process_bayer_images(
				self.input_paths,
				self.output_entry.get(),
				self.mode_var.get(),
				self.compression_scale.get(),
				self.header_footer_var.get(),
				series_name,
			)
			self.set_status("Done", color="green")
		except Exception as e:
			self.set_status(f"Exception: {e}", color="red")
		finally:
			self.start_button.config(state=tk.NORMAL)


class ShiftRightImageTab(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		self.create_widgets()

	def create_widgets(self):
		# Input file
		file_frame = tk.LabelFrame(self, text="Input .bin file")
		file_frame.pack(fill=tk.X, padx=10, pady=5)
		self.input_entry = tk.Entry(file_frame, width=50)
		self.input_entry.pack(side=tk.LEFT, padx=5, pady=5)
		tk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=5)

		# Shift count
		shift_frame = tk.LabelFrame(self, text="Shift count (bytes)")
		shift_frame.pack(fill=tk.X, padx=10, pady=5)
		self.shift_entry = tk.Entry(shift_frame, width=10)
		self.shift_entry.pack(side=tk.LEFT, padx=5, pady=5)
		self.shift_entry.insert(0, "1")

		# Start row/col
		rowcol_frame = tk.LabelFrame(self, text="Start row / Start col")
		rowcol_frame.pack(fill=tk.X, padx=10, pady=5)
		self.row_entry = tk.Entry(rowcol_frame, width=10)
		self.row_entry.pack(side=tk.LEFT, padx=5, pady=5)
		self.row_entry.insert(0, "0")
		self.col_entry = tk.Entry(rowcol_frame, width=10)
		self.col_entry.pack(side=tk.LEFT, padx=5, pady=5)
		self.col_entry.insert(0, "0")

		# Image width/height (optional)
		wh_frame = tk.LabelFrame(self, text="Image width / height (optional)")
		wh_frame.pack(fill=tk.X, padx=10, pady=5)
		self.width_entry = tk.Entry(wh_frame, width=10)
		self.width_entry.pack(side=tk.LEFT, padx=5, pady=5)
		self.width_entry.insert(0, "4096")
		self.height_entry = tk.Entry(wh_frame, width=10)
		self.height_entry.pack(side=tk.LEFT, padx=5, pady=5)
		self.height_entry.insert(0, "4098")

		# Status
		self.status_label = tk.Label(self, text="Ready", fg="blue")
		self.status_label.pack(pady=2)

		# Start button
		self.start_button = tk.Button(self, text="Shift Image", command=self.start_processing)
		self.start_button.pack(pady=10)

	def browse_file(self):
		f = filedialog.askopenfilename(title="Select .bin file", filetypes=[("Binary files", "*.bin")])
		if f:
			self.input_entry.delete(0, tk.END)
			self.input_entry.insert(0, f)

	def set_status(self, msg, color="blue"):
		self.status_label.config(text=msg, fg=color)

	def start_processing(self):
		img_file = self.input_entry.get()
		shift_count = self.shift_entry.get()
		start_row = self.row_entry.get()
		start_col = self.col_entry.get()
		img_width = self.width_entry.get()
		img_height = self.height_entry.get()
		if not img_file or not shift_count or not start_row:
			self.set_status("Please fill all required fields", color="red")
			return
		args = [os.path.join(os.path.dirname(__file__), "shiftRightImage.py"), img_file, shift_count, start_row]
		if start_col:
			args.append(start_col)
		if img_width and img_height:
			args.extend([img_width, img_height])
		self.start_button.config(state=tk.DISABLED)
		self.set_status("Processing...", color="orange")
		thread = threading.Thread(target=self.run_process, args=(args,))
		thread.start()

	def run_process(self, args):
		try:
			# args: [img_file, shift_count, start_row, start_col, img_width, img_height]
			img_file = args[1]
			shift_count = int(args[2])
			start_row = int(args[3])
			start_col = int(args[4]) if len(args) > 4 else 0
			img_width = int(args[5]) if len(args) > 5 else 4096
			img_height = int(args[6]) if len(args) > 6 else 4098
			ret = shift_right_image_file(img_file, shift_count, start_row, start_col, img_width, img_height)
			if ret == 0:
				self.set_status("Done", color="green")
			else:
				self.set_status(f"Error: return code {ret}", color="red")
		except Exception as e:
			self.set_status(f"Exception: {e}", color="red")
		finally:
			self.start_button.config(state=tk.NORMAL)


class DetectAndFixShiftTab(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		self.create_widgets()

	def create_widgets(self):
		# Input file
		file_frame = tk.LabelFrame(self, text="Input .bin file")
		file_frame.pack(fill=tk.X, padx=10, pady=5)
		self.input_entry = tk.Entry(file_frame, width=50)
		self.input_entry.pack(side=tk.LEFT, padx=5, pady=5)
		tk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=5)

		# Output file
		out_frame = tk.LabelFrame(self, text="Output fixed .bin file")
		out_frame.pack(fill=tk.X, padx=10, pady=5)
		self.output_entry = tk.Entry(out_frame, width=50)
		self.output_entry.pack(side=tk.LEFT, padx=5, pady=5)
		tk.Button(out_frame, text="Browse", command=self.browse_output_file).pack(side=tk.LEFT, padx=5)

		# Status
		self.status_label = tk.Label(self, text="Ready", fg="blue")
		self.status_label.pack(pady=2)

		# Start button
		self.start_button = tk.Button(self, text="Detect and Fix Shift", command=self.start_processing)
		self.start_button.pack(pady=10)

	def browse_file(self):
		f = filedialog.askopenfilename(title="Select .bin file", filetypes=[("Binary files", "*.bin")])
		if f:
			self.input_entry.delete(0, tk.END)
			self.input_entry.insert(0, f)

	def browse_output_file(self):
		f = filedialog.asksaveasfilename(title="Save fixed .bin file as", defaultextension=".bin", filetypes=[("Binary files", "*.bin")])
		if f:
			self.output_entry.delete(0, tk.END)
			self.output_entry.insert(0, f)

	def set_status(self, msg, color="blue"):
		self.status_label.config(text=msg, fg=color)

	def start_processing(self):
		input_file = self.input_entry.get()
		output_file = self.output_entry.get()
		if not input_file or not output_file:
			self.set_status("Please select input and output files", color="red")
			return
		args = [os.path.join(os.path.dirname(__file__), "detectAndFixShift.py"), input_file, output_file]
		self.start_button.config(state=tk.DISABLED)
		self.set_status("Processing...", color="orange")
		thread = threading.Thread(target=self.run_process, args=(args,))
		thread.start()

	def run_process(self, args):
		try:
			# args: [input_file, output_file]
			input_file = args[1]
			output_file = args[2]
			detect_and_fix_shift(input_file, output_file)
			self.set_status("Done", color="green")
		except Exception as e:
			self.set_status(f"Exception: {e}", color="red")
		finally:
			self.start_button.config(state=tk.NORMAL)


def resource_path(relative_path):
	# Get absolute path to resource, works for dev and for PyInstaller
	if hasattr(sys, '_MEIPASS'):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.dirname(__file__), relative_path)

def main():
	root = tk.Tk()
	import platform
	system = platform.system()
	if system == "Windows":
		icon_path = resource_path("assets/bip-icon.ico")
		try:
			root.iconbitmap(icon_path)
		except Exception as e:
			print(f"Warning: Could not set window icon: {e}")
	else:
		icon_path = resource_path("assets/bip-icon.png")
		try:
			img = tk.PhotoImage(file=icon_path)
			root.iconphoto(True, img)
		except Exception as e:
			print(f"Warning: Could not set window icon: {e}")
	root.title("Bayer Image Processor")
	style = Style("flatly")
	notebook = ttk.Notebook(root)
	notebook.pack(fill=tk.BOTH, expand=True)

	tab1 = BayerImageProcessorTab(notebook)
	tab2 = ShiftRightImageTab(notebook)
	tab3 = DetectAndFixShiftTab(notebook)
	notebook.add(tab1, text="Binary To PNG")
	notebook.add(tab2, text="Shift Right Image")
	notebook.add(tab3, text="Detect & Fix Shift")

	root.minsize(600, 500)
	root.mainloop()


if __name__ == "__main__":
	main()
