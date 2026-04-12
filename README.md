# 🎮 ROMOrgan

An automated, intelligent Python pipeline with a native GUI designed to sort, extract, verify, and aggressively compress retro video game ROMs and disc images. 

Instead of manually sorting through terabytes of messy `.zip`, `.7z`, `.bin/.cue`, and `.iso` files, this tool uses a custom heuristic engine, database hash-matching, and deep boot-sector scanning to perfectly identify games, move them to their correct console folders, and automatically compress them into modern formats (`.chd`, `.cso`, `.rvz`) to save hard drive space.

## ✨ Features

* **Native GUI:** A clean, built-in Tkinter interface that lets you select input/output folders and watch the live logs without freezing.
* **Smart Extraction:** Automatically extracts archives (`.zip`, `.7z`, etc.) into a temporary workspace.
* **Advanced Heuristic Engine:** Routes games based on extension, file size thresholds, and naming conventions.
* **Deep Serial Scanning:** Reads the first 2MB of an `.iso` file to find hidden internal serial numbers (e.g., `SLUS-20001`, `NPJH-50443`) to perfectly identify ambiguous PS1, PS2, PSP, GameCube, and Wii games.
* **Hash Verification:** Falls back to MD5 hashing against a local JSON database (`titles_db.json`) for exact title matches.
* **Automated Compression:** Triggers external C++ tools (`chdman`, `maxcso`, `dolphintool`) to compress heavy optical media.
* **Bulletproof Cleanup:** Intelligently reads inside `.cue` files to precisely delete leftover `.bin` tracks after successful compression, gracefully navigating Windows file locks.

---

## 📂 Project Structure

The project is broken down into specialized modules that handle specific parts of the pipeline:

* **`main.py`**: The entry point. Houses the Tkinter GUI, sets up global logging, and orchestrates the entire pipeline from start to finish.
* **`rules.py`**: Loads the necessary dictionaries (extensions, sizes, console tags) from external `.txt` files.
* **`scanner.py`**: Crawls the input directory to find all available files.
* **`classifier.py`**: The brain of the operation. Determines if a file is a ROM, an archive to be extracted, or trash.
* **`extractor.py`**: Safely unzips archives into a temporary directory and queues the internal files for re-classification.
* **`processor.py`**: Runs the Heuristic Engine, Deep Serial Scanner, and Hash Matcher to perfectly identify the target console. Moves files to `ROMs/` or `to_compress/`.
* **`compressor.py`**: Spawns background subprocesses to run `chdman`, `maxcso`, or `dolphintool`. Handles the safe deletion of original uncompressed files upon success.
* **`cleaner.py`**: Sweeps the directory at the end of the process to remove any empty leftover folders safely.

---

## 🛠️ Prerequisites & Setup

### 1. Python Requirements
This script requires **Python 3.8+**. It uses standard library modules (`tkinter`, `pathlib`, `subprocess`, `logging`, `hashlib`, `re`, `shutil`), so no massive `pip install` packages are required for the core logic (though `patool` or similar may be required depending on your `extractor.py` implementation).

### 2. Required Text & JSON Files
Ensure the following rule files are located in the same directory as `main.py`:
* `valid_suffix.txt`
* `suffix_sizes.txt`
* `console_tags_serials.txt`
* `titles_db.json` (Used for hash matching)

### 3. External Compression Tools
To allow the script to compress games, you must place the required `.exe` files in a `tools` directory right next to `main.py`.

Your folder structure **must** look exactly like this:

```text
📁 Your_Project_Folder/
 ├── 📄 main.py
 ├── 📄 processor.py
 ├── 📄 ... (other python files and .txt files)
 └── 📁 tools/
      ├── 📄 chdman.exe      <-- (Used for PS1, PS2, Saturn, SegaCD, Dreamcast)
      ├── 📄 maxcso.exe      <-- (Used for PSP)
      └── 📁 Dolphin-x64/    <-- (The full Dolphin Emulator folder, used for GC/Wii)
           ├── 📄 DolphinTool.exe
           ├── 📄 Qt6Core.dll
           └── 📁 Sys/
---

## 🚀 How to Use

1. Double-click **`main.py`** (or run `python main.py` in your terminal).
2. The ROM Organizer window will appear.
3. **Input Directory:** Select the folder containing your messy ROMs, `.zip` files, and `.iso` dumps.
4. **Output Directory:** Select the destination folder where you want your clean, organized `ROMs` folder to be generated.
5. Click **START ORGANIZING**.
6. A progress window will appear. The script runs on a background thread, streaming live logs to the UI so you can watch it extract, match, move, and compress your library in real-time.

---

## ⚙️ How the Pipeline Works (The Flow)

1. **Scan:** Reads all files in the Input Directory.
2. **First Pass Classification:** Identifies immediate ROMs vs. Archives.
3. **Extraction:** Archives are unpacked. Extracted contents are fed *back* into the classifier.
4. **Processing & Routing:** * If a file is a cartridge game (`.nes`, `.sfc`), it goes straight to the Output `ROMs/` folder.
    * If a file is uncompressed optical media (`.iso`, `.bin/.cue`, `.gdi`), it is identified via heuristics/deep-scanning and routed to a staging folder (e.g., `to_compress/PS2_to_compress/`).
5. **Compression:** The script loops through the staging folders, firing off the correct command-line tool (`createcd`, `convert -f rvz`, `--out cso`).
6. **Self-Healing Cleanup:** Upon a successful compression (Return Code 0), the script parses the original `.cue` files to find exact track names, waits for Windows to release file locks, deletes the heavy uncompressed `.bin`/`.iso` files, and moves the new `.chd`/`.rvz` to the final `ROMs/` folder.
7. **Sweep:** Empty staging folders are silently removed.
