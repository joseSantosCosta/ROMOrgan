import sys
import os
import threading
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

import rules
import scanner
import classifier
import extractor
import processor
import compressor
import cleaner


if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent.absolute()


logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("main.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)



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
            self.text_widget.see(tk.END)
        self.text_widget.after(0, append)



class ROMOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ROM Organizer v1.0")
        self.root.geometry("550x320")

        
        self.BG = "#0b0b0b"
        self.FG = "#00ff9c"
        self.ACCENT = "#00cc7a"
        self.BTN_BG = "#111111"

        self.root.configure(bg=self.BG, padx=20, pady=20)

        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()

        self.build_main_window()

    def verify_tools(self):
        tools_dir = BASE_DIR / "tools"

        required_tools = {
            "CHDMAN": tools_dir / "chdman.exe",
            "MaxCSO": tools_dir / "maxcso.exe",
            "DolphinTool": tools_dir / "Dolphin-x64" / "DolphinTool.exe",
            "UnRAR": tools_dir / "UnRar.exe"
        }

        return [name for name, path in required_tools.items() if not path.exists()]

    def build_main_window(self):
        font_main = ("Courier New", 10)
        font_title = ("Courier New", 11, "bold")

        tk.Label(self.root, text="> INPUT DIRECTORY", bg=self.BG, fg=self.FG, font=font_title).pack(anchor="w")
        input_frame = tk.Frame(self.root, bg=self.BG)
        input_frame.pack(fill="x", pady=(5, 15))

        tk.Entry(input_frame, textvariable=self.input_path_var, bg="#000", fg=self.FG,
                 insertbackground=self.FG, relief="flat", font=font_main)\
            .pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Button(input_frame, text="[ BROWSE ]", bg=self.BTN_BG, fg=self.ACCENT,
                  relief="flat", command=self.browse_input)\
            .pack(side="right")

       
        tk.Label(self.root, text="> OUTPUT DIRECTORY", bg=self.BG, fg=self.FG, font=font_title).pack(anchor="w")
        output_frame = tk.Frame(self.root, bg=self.BG)
        output_frame.pack(fill="x", pady=(5, 20))

        tk.Entry(output_frame, textvariable=self.output_path_var, bg="#000", fg=self.FG,
                 insertbackground=self.FG, relief="flat", font=font_main)\
            .pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Button(output_frame, text="[ BROWSE ]", bg=self.BTN_BG, fg=self.ACCENT,
                  relief="flat", command=self.browse_output)\
            .pack(side="right")

        
        tk.Button(self.root, text=">>> START <<<", bg="#001a12", fg=self.FG,
                  font=("Courier New", 12, "bold"), relief="flat",
                  command=self.start_process)\
            .pack(pady=20, ipadx=10, ipady=10)

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path_var.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path_var.set(folder)

    def start_process(self):
        input_dir = self.input_path_var.get()
        output_dir = self.output_path_var.get()

        if not input_dir or not output_dir:
            tk.messagebox.showwarning("Missing Folders", "Select both folders.")
            return

        missing = self.verify_tools()
        if missing:
            tk.messagebox.showerror("Missing Tools", f"Missing:\n" + "\n".join(missing))
            return

        self.root.withdraw()
        self.build_progress_window()

        threading.Thread(
            target=self.run_backend_script,
            args=(input_dir, output_dir),
            daemon=True
        ).start()

    def build_progress_window(self):
        self.prog_win = tk.Toplevel(self.root)
        self.prog_win.title("PROCESSING")
        self.prog_win.geometry("700x450")
        self.prog_win.configure(bg=self.BG, padx=20, pady=20)

        self.prog_win.protocol("WM_DELETE_WINDOW", self.root.destroy)

        tk.Label(self.prog_win, text="> RUNNING PIPELINE...", bg=self.BG,
                 fg=self.FG, font=("Courier New", 11, "bold")).pack(anchor="w")

        self.progress_bar = ttk.Progressbar(self.prog_win, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=(5, 15))
        self.progress_bar.start(10)

        tk.Label(self.prog_win, text="> LOG OUTPUT", bg=self.BG,
                 fg=self.FG, font=("Courier New", 11, "bold")).pack(anchor="w")

        self.log_area = scrolledtext.ScrolledText(
            self.prog_win,
            state='disabled',
            bg="#000",
            fg=self.FG,
            insertbackground=self.FG,
            font=("Courier New", 9),
            relief="flat"
        )
        self.log_area.pack(fill="both", expand=True)

        # Prevent duplicate handlers
        logger = logging.getLogger()
        logger.handlers = [h for h in logger.handlers if not isinstance(h, TextHandler)]

        text_handler = TextHandler(self.log_area)
        text_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logger.addHandler(text_handler)

     
    def run_backend_script(self, input_dir, output_dir):
        try:
            logging.info("BOOTING ROM ORGANIZER...")

            logging.info("Loading rules...")
            files_type_dict = rules.create_file_types_dict()
            valid_suffix_dict = rules.create_valid_suffix_dict(BASE_DIR / 'valid_suffix.txt')
            suffix_size_dict = rules.create_suffix_size_dict(BASE_DIR / 'suffix_sizes.txt')
            console_tag_serial_dict = rules.create_tag_serial_dict(BASE_DIR / 'console_tags_serials.txt')
            tempDir, extracted_list = rules.create_extracted_temp()

            logging.info("Scanning directory...")
            files = scanner.scan_directory(Path(input_dir))

            classifier.classify_files(files, files_type_dict, valid_suffix_dict)

            while files_type_dict['to_extract']:
                copy_list = files_type_dict['to_extract'].copy()
                files_type_dict['to_extract'].clear()
                extracted_list.clear()
                extractor.get_archive_files(copy_list, tempDir, extracted_list)
                classifier.classify_files(extracted_list, files_type_dict, valid_suffix_dict)

            os.chdir(output_dir)
            logging.info("Output directory set.")

            processor.create_folders()
            processor.processor(files_type_dict, tempDir, suffix_size_dict, console_tag_serial_dict)

            compressor.compressor()
            cleaner.clean_empty(Path())

            logging.info(">>> COMPLETE <<<")

        except Exception as e:
            logging.error(f"FATAL ERROR: {e}", exc_info=True)

        finally:
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate', value=100)



if __name__ == "__main__":
    root = tk.Tk()
    app = ROMOrganizerApp(root)
    root.mainloop()