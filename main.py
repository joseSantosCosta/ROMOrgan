import sys
import os
import time
import threading
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

# --- HOME MADE MODULES ---
import rules
import scanner
import classifier
import extractor
import processor
import compressor
import cleaner

import sys
import os

if getattr(sys, 'frozen', False):
    # If running as a bundled exe, use the exe's folder
    BASE_DIR = Path(sys._MEIPASS)
else:
    # If running as a script, use the script's folder
    BASE_DIR = Path(__file__).parent.absolute()


root_logger = logging.getLogger()


if root_logger.hasHandlers():
    root_logger.handlers.clear()


root_logger.setLevel(logging.INFO)


logging.basicConfig(
    level=logging.INFO, 
    format='%(levelname)s: %(message)s',
    force=True, # This is the magic keyword for Python 3.8+
    handlers=[
        logging.FileHandler("main.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ])

# --- 2. GUI TEXT HANDLER ---
# This intercepts the logs and pushes them to the UI text box
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.see(tk.END) # Auto-scroll to bottom
        self.text_widget.after(0, append)


# --- 3. MAIN APPLICATION CLASS ---
class ROMOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ROM Organizer & Compressor")
        self.root.geometry("550x300")
        self.root.configure(padx=20, pady=20)

        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()

        self.build_main_window()

    def build_main_window(self):
        # Input Section
        tk.Label(self.root, text="Select Input Directory (Where your messy files are):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill="x", pady=(0, 15))
        tk.Entry(input_frame, textvariable=self.input_path_var, width=50, state="readonly").pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Button(input_frame, text="Browse", command=self.browse_input).pack(side="right")

        # Output Section
        tk.Label(self.root, text="Select Output Directory (Where the ROMs folder will go):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill="x", pady=(0, 20))
        tk.Entry(output_frame, textvariable=self.output_path_var, width=50, state="readonly").pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Button(output_frame, text="Browse", command=self.browse_output).pack(side="right")

        # Green Start Button
        style = ttk.Style()
        style.configure("Green.TButton", font=("Arial", 12, "bold"), foreground="green")
        self.start_btn = ttk.Button(self.root, text="START ORGANIZING", style="Green.TButton", command=self.start_process)
        self.start_btn.pack(pady=20, ipadx=20, ipady=10)

    def browse_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder: self.input_path_var.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder: self.output_path_var.set(folder)

    def start_process(self):
        input_dir = self.input_path_var.get()
        output_dir = self.output_path_var.get()

        if not input_dir or not output_dir:
            tk.messagebox.showwarning("Missing Folders", "Please select both an Input and Output directory!")
            return

        self.root.withdraw() # Hide main window
        self.build_progress_window() # Show progress window

        # Start your script in a background thread so the UI doesn't freeze!
        threading.Thread(target=self.run_backend_script, args=(input_dir, output_dir), daemon=True).start()

    def build_progress_window(self):
        self.prog_win = tk.Toplevel(self.root)
        self.prog_win.title("Processing ROMs...")
        self.prog_win.geometry("700x450")
        self.prog_win.configure(padx=20, pady=20)
        self.prog_win.protocol("WM_DELETE_WINDOW", self.root.destroy)

        tk.Label(self.prog_win, text="Progress:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.progress_bar = ttk.Progressbar(self.prog_win, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=(5, 15))
        self.progress_bar.start(15)

        tk.Label(self.prog_win, text="Activity Log:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.log_area = scrolledtext.ScrolledText(self.prog_win, state='disabled', bg="black", fg="lime", font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True)

        # Hook the UI text box into our logging system
        text_handler = TextHandler(self.log_area)
        text_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logging.getLogger().addHandler(text_handler)


    # --- 4. YOUR PIPELINE LOGIC ---
    def run_backend_script(self, input_dir, output_dir):
        try:
            logging.info("--- STARTING ROM ORGANIZER ---")
            
            # Determine base directory so we can always find the .txt files
            BASE_DIR = Path(__file__).parent.absolute()
            
            logging.info("Loading rule dictionaries...")
            files_type_dict = rules.create_file_types_dict()
            valid_suffix_dict = rules.create_valid_suffix_dict(BASE_DIR / 'valid_suffix.txt')
            suffix_size_dict = rules.create_suffix_size_dict(BASE_DIR / 'suffix_sizes.txt')
            console_tag_serial_dict = rules.create_tag_serial_dict(BASE_DIR / 'console_tags_serials.txt')
            tempDir, extracted_list = rules.create_extracted_temp()

            # 1. Scan Input Directory
            logging.info(f"Scanning input directory: {input_dir}")
            dir_to_scan = Path(input_dir)
            files = scanner.scan_directory(dir_to_scan)

            # 2. First Classification
            classifier.classify_files(files, files_type_dict, valid_suffix_dict)

            # 3. Extraction Loop
            while files_type_dict['to_extract']:
                copy_to_extract_files = files_type_dict['to_extract'].copy()
                files_type_dict['to_extract'].clear()
                extracted_list.clear() 
                extractor.get_archive_files(copy_to_extract_files, tempDir, extracted_list)
                classifier.classify_files(extracted_list, files_type_dict, valid_suffix_dict)

            # --- THE LIFEHACK ---
            # We change the virtual working directory to the user's Output Folder!
            # Now, when processor.py says Path() / 'ROMs', it will create it in the output folder.
            os.chdir(output_dir)
            logging.info(f"Working directory changed to Output Folder: {output_dir}")

            # 4. Process and Move Files
            processor.create_folders() 
            processor.processor(files_type_dict, tempDir, suffix_size_dict, console_tag_serial_dict)

            # 5. Compress
            compressor.compressor()

            # 6. Clean Up
            cleaner.clean_empty(Path())

            logging.info("✅ ALL TASKS COMPLETED SUCCESSFULLY!")

        except Exception as e:
            logging.error(f"❌ A FATAL ERROR OCCURRED: {e}", exc_info=True)
            
        finally:
            # Stop the bouncing progress bar
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate', value=100)


# --- 5. EXECUTION ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ROMOrganizerApp(root)
    root.mainloop()