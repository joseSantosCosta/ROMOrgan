import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import logging
import time

# --- CUSTOM LOG HANDLER ---
# This intercepts standard Python logging and routes it to our UI text box
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
            self.text_widget.see(tk.END) # Auto-scroll to the bottom
        # Use .after to safely update the UI from a background thread
        self.text_widget.after(0, append)


# --- MAIN APPLICATION CLASS ---
class ROMOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ROM Organizer & Compressor")
        self.root.geometry("500x300")
        self.root.configure(padx=20, pady=20)

        # Variables to store the selected paths
        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()

        self.build_main_window()

    def build_main_window(self):
        # --- INPUT FOLDER SECTION ---
        tk.Label(self.root, text="Select Input Directory (Where your messy files are):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill="x", pady=(0, 15))
        
        tk.Entry(input_frame, textvariable=self.input_path_var, width=50, state="readonly").pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Button(input_frame, text="Browse", command=self.browse_input).pack(side="right")

        # --- OUTPUT FOLDER SECTION ---
        tk.Label(self.root, text="Select Output Directory (Where the ROMs folder will go):", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill="x", pady=(0, 20))
        
        tk.Entry(output_frame, textvariable=self.output_path_var, width=50, state="readonly").pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Button(output_frame, text="Browse", command=self.browse_output).pack(side="right")

        # --- GREEN START BUTTON ---
        # Styling the button to match your wireframe
        style = ttk.Style()
        style.configure("Green.TButton", font=("Arial", 12, "bold"), foreground="green")
        
        self.start_btn = ttk.Button(self.root, text="START ORGANIZING", style="Green.TButton", command=self.start_process)
        self.start_btn.pack(pady=20, ipadx=20, ipady=10)

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

        # 1. Hide the main window
        self.root.withdraw()

        # 2. Build the Progress Window
        self.build_progress_window()

        # 3. Start the actual script in a separate background thread!
        # (If you don't use threading here, the whole UI will freeze while CHDMAN runs)
        threading.Thread(target=self.run_backend_script, args=(input_dir, output_dir), daemon=True).start()

    def build_progress_window(self):
        self.prog_win = tk.Toplevel(self.root)
        self.prog_win.title("Processing ROMs...")
        self.prog_win.geometry("600x400")
        self.prog_win.configure(padx=20, pady=20)
        
        # If user closes the progress window, kill the whole app
        self.prog_win.protocol("WM_DELETE_WINDOW", self.root.destroy)

        # Progress Bar
        tk.Label(self.prog_win, text="Progress:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.progress_bar = ttk.Progressbar(self.prog_win, mode='indeterminate') # Indeterminate makes it bounce back and forth
        self.progress_bar.pack(fill="x", pady=(5, 15))
        self.progress_bar.start(15) # Start the animation

        # Log Text Box
        tk.Label(self.prog_win, text="Activity Log:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.log_area = scrolledtext.ScrolledText(self.prog_win, state='disabled', bg="black", fg="lime", font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True)

        # Connect Python's standard logging to our text box
        text_handler = TextHandler(self.log_area)
        text_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logging.getLogger().addHandler(text_handler)
        logging.getLogger().setLevel(logging.INFO)

    def run_backend_script(self, input_dir, output_dir):
        """
        THIS IS WHERE YOU CONNECT YOUR SCRIPT!
        Everything in here runs in the background so the UI doesn't freeze.
        """
        logging.info(f"Starting pipeline...")
        logging.info(f"Input: {input_dir}")
        logging.info(f"Output: {output_dir}")
        
        try:
            # --- REPLACE THIS DUMMY CODE WITH YOUR ACTUAL MAIN.PY CALLS ---
            # Example of how you would link it:
            # import scanner
            # import processor
            # scanner.scan(input_dir)
            # processor.run(output_dir)
            
            # Simulated work to show you how the UI reacts
            for i in range(1, 6):
                time.sleep(1.5)
                logging.info(f"Extracting file {i}...")
                
            logging.info("Hashing files to check against Database...")
            time.sleep(2)
            
            logging.info("Triggering CHDMAN compression for PS2 games...")
            time.sleep(3)
            # --------------------------------------------------------------

            logging.info("✅ ALL PROCESSES COMPLETE!")
            
        except Exception as e:
            logging.error(f"❌ A fatal error occurred: {e}")
            
        finally:
            # Stop the bouncing progress bar when finished
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate', value=100)


# --- LAUNCH THE APP ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ROMOrganizerApp(root)
    root.mainloop()