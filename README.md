#  ROMOrgan (still in progress)

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

##  Project Structure

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

##  Prerequisites & Setup

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
```

### 4. Downloading the Required Tools
Due to licensing and file size limits, the external compression and extraction tools are not bundled with this script. You will need to download them and place them in the `tools/` folder as shown above.

* **[7-Zip](https://www.7-zip.org/) (System Install):** Highly recommended. The Python extraction engine relies on your system's archivers. Install 7-Zip normally on your Windows machine to ensure `.7z` and `.zip` files are handled smoothly.
* **[UnRAR for Windows](https://www.rarlab.com/rar_add.htm):** Required if you have `.rar` files in your collection. Download the "UnRAR for Windows" command-line utility and place `UnRar.exe` directly inside your `tools/` folder.
* **[CHDMAN](https://www.mamedev.org/release.html):** The industry standard for optical media compression. CHDMAN is officially distributed as part of the MAME emulator. Download the latest MAME release, extract it, find `chdman.exe` inside, and copy it to your `tools/` folder.
* **[MaxCSO](https://github.com/unknownbrackets/maxcso/releases):** The fastest and most efficient PSP ISO compressor. Go to the official GitHub Releases page, download the latest Windows `.zip`, and extract `maxcso.exe` to your `tools/` folder.
* **[Dolphin Emulator](https://dolphin-emu.org/download/):** Required for converting GameCube and Wii games to `.rvz`. Download the latest Beta or Development version of Dolphin (Windows x64). Extract the entire folder, rename it to `Dolphin-x64`, and place the whole folder inside your `tools/` directory. *(Ensure `DolphinTool.exe` is inside it!)*

##  How to Use

### If using the Standalone App (.exe)
1. Download the latest ZIP from the **Releases** tab and extract it.
2. Ensure you have downloaded the required external tools (Dolphin, etc.) and placed them in the `tools/` folder.
3. Double-click **`ROMOrganizer.exe`** to launch the application.

### If running from Source (Python)
1. Ensure you have Python 3.8+ installed.
2. Open your terminal in the project folder and run: `python main.py`

###  The Organizing Process
Once the application window is open, the process is incredibly simple:

1. **Input Directory:** Click "Browse" and select the folder containing your messy, unorganized files (e.g., your generic "Downloads" folder filled with `.zip` files, `.iso` dumps, and `.bin/.cue` sets).
2. **Output Directory:** Click "Browse" and select your clean destination folder (e.g., your external hard drive or emulator frontend folder). *Note: The app will automatically create a `ROMs` subfolder inside this destination.*
3. **Start:** Click the **START ORGANIZING** button.
4. **Watch the Magic:** A progress window will appear. The tool will automatically begin extracting archives, identifying games, routing them to the correct console folders, and running the compression tools. You can watch the live log feed to see exactly what the engine is doing!
