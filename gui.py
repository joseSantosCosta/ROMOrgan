import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import logging
import time

# --- CUSTOM LOG HANDLER ---
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


# --- MAIN APPLICATION CLASS ---
class ROMOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ROM Organizer v1.0")
        self.root.geometry("520x320")

        # --- RETRO COLORS ---
        self.BG = "#0b0b0b"
        self.FG = "#00ff9c"
        self.ACCENT = "#00cc7a"
        self.BTN_BG = "#111111"

        self.root.configure(bg=self.BG, padx=20, pady=20)

        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()

        self.build_main_window()

    def build_main_window(self):
        font_main = ("Courier New", 10)
        font_title = ("Courier New", 11, "bold")

        # --- INPUT SECTION ---
        tk.Label(self.root, text="> SELECT INPUT DIRECTORY", bg=self.BG, fg=self.FG, font=font_title).pack(anchor="w", pady=(0, 5))
        
        input_frame = tk.Frame(self.root, bg=self.BG)
        input_frame.pack(fill="x", pady=(0, 15))

        tk.Entry(
            input_frame,
            textvariable=self.input_path_var,
            bg="#000000",
            fg=self.FG,
            insertbackground=self.FG,
            relief="flat",
            font=font_main
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Button(
            input_frame,
            text="[ BROWSE ]",
            bg=self.BTN_BG,
            fg=self.ACCENT,
            activebackground=self.ACCENT,
            activeforeground="black",
            relief="flat",
            command=self.browse_input
        ).pack(side="right")

        # --- OUTPUT SECTION ---
        tk.Label(self.root, text="> SELECT OUTPUT DIRECTORY", bg=self.BG, fg=self.FG, font=font_title).pack(anchor="w", pady=(0, 5))

        output_frame = tk.Frame(self.root, bg=self.BG)
        output_frame.pack(fill="x", pady=(0, 20))

        tk.Entry(
            output_frame,
            textvariable=self.output_path_var,
            bg="#000000",
            fg=self.FG,
            insertbackground=self.FG,
            relief="flat",
            font=font_main
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Button(
            output_frame,
            text="[ BROWSE ]",
            bg=self.BTN_BG,
            fg=self.ACCENT,
            activebackground=self.ACCENT,
            activeforeground="black",
            relief="flat",
            command=self.browse_output
        ).pack(side="right")

        # --- START BUTTON ---
        self.start_btn = tk.Button(
            self.root,
            text=">>> START PROCESS <<<",
            bg="#001a12",
            fg=self.FG,
            activebackground=self.FG,
            activeforeground="black",
            font=("Courier New", 12, "bold"),
            relief="flat",
            command=self.start_process
        )
        self.start_btn.pack(pady=20, ipadx=10, ipady=10)

    def browse_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_path_var.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path_var.set(folder)

    def start_process(self):
        input_dir = self.input_path_var.get()
        output_dir = self.output_path_var.get()

        if not input_dir or not output_dir:
            tk.messagebox.showwarning("Missing Folders", "Please select both an Input and Output directory!")
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
        self.prog_win.title("ROM PROCESSOR")
        self.prog_win.geometry("700x450")
        self.prog_win.configure(bg=self.BG, padx=20, pady=20)

        self.prog_win.protocol("WM_DELETE_WINDOW", self.root.destroy)

        tk.Label(
            self.prog_win,
            text="> PROCESSING...",
            bg=self.BG,
            fg=self.FG,
            font=("Courier New", 11, "bold")
        ).pack(anchor="w")

        self.progress_bar = ttk.Progressbar(self.prog_win, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=(5, 15))
        self.progress_bar.start(10)

        tk.Label(
            self.prog_win,
            text="> SYSTEM LOG",
            bg=self.BG,
            fg=self.FG,
            font=("Courier New", 11, "bold")
        ).pack(anchor="w")

        self.log_area = scrolledtext.ScrolledText(
            self.prog_win,
            state='disabled',
            bg="#000000",
            fg="#00ff9c",
            insertbackground="#00ff9c",
            font=("Courier New", 9),
            relief="flat"
        )
        self.log_area.pack(fill="both", expand=True)

        text_handler = TextHandler(self.log_area)
        text_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logging.getLogger().addHandler(text_handler)
        logging.getLogger().setLevel(logging.INFO)

    def run_backend_script(self, input_dir, output_dir):
        logging.info("BOOTING ROM PIPELINE...")
        logging.info(f"INPUT  -> {input_dir}")
        logging.info(f"OUTPUT -> {output_dir}")

        try:
            for i in range(1, 6):
                time.sleep(1.5)
                logging.info(f"EXTRACTING FILE {i}...")

            logging.info("HASHING FILES...")
            time.sleep(2)

            logging.info("RUNNING COMPRESSION...")
            time.sleep(3)

            logging.info(">>> ALL PROCESSES COMPLETE <<<")

        except Exception as e:
            logging.error(f"FATAL ERROR: {e}")

        finally:
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate', value=100)


# --- LAUNCH ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ROMOrganizerApp(root)
    root.mainloop()