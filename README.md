# ROMOrgan

> Work in progress. The core pipeline is fully functional and capable of building a clean, organized ROM library from scratch. Active development is now focused on adding support for existing libraries created by the user.

An automated, intelligent Python pipeline with a native GUI to sort, extract, identify, and compress retro video game ROMs and disc images.

Instead of manually sorting through terabytes of messy `.zip`, `.7z`, `.bin/.cue`, and `.iso` files, ROMOrgan uses a custom heuristic engine, database hash-matching, and deep boot-sector scanning to perfectly identify games, move them to the correct console folders, and automatically compress them into modern formats (`.chd`, `.cso`, `.rvz`) — saving significant hard drive space.

---

## Features

- **Native GUI** — A clean Tkinter interface to select input/output folders and watch live logs without freezing.
- **Smart Extraction** — Automatically extracts archives (`.zip`, `.7z`, `.rar`, etc.) into a temporary workspace before processing.
- **Advanced Heuristic Engine** — Routes games based on file extension, size thresholds, and naming conventions.
- **Deep Serial Scanning** — Reads the first 2MB of `.iso` files to find hidden internal serial numbers (e.g., `SLUS-20001`, `NPJH-50443`) to perfectly identify ambiguous PS1, PS2, PSP, GameCube, and Wii games.
- **Hash Verification** — Falls back to MD5 hashing against a local JSON database (`titles_db.json`) for exact title matches.
- **Automated Compression** — Triggers external tools (`chdman`, `maxcso`, `dolphintool`) to compress heavy optical media into modern formats.
- **Bulletproof Cleanup** — Reads inside `.cue` files to precisely delete leftover `.bin` tracks after successful compression, gracefully navigating Windows file locks.

---

## Project Structure

| File | Role |
|---|---|
| `main.py` | Entry point. Sets up logging and orchestrates the full pipeline. |
| `gui.py` | Tkinter GUI definition and event handling. |
| `GUI_creator.py` | GUI component builder helpers. |
| `rules.py` | Loads extension/size/console-tag dictionaries from `.txt` files. |
| `scanner.py` | Crawls the input directory to find all available files. |
| `classifier.py` | The brain — determines if a file is a ROM, an archive, or trash. |
| `extractor.py` | Safely extracts archives into a temp directory and queues files for re-classification. |
| `processor.py` | Runs the Heuristic Engine, Deep Serial Scanner, and Hash Matcher to identify the target console. Moves files to `ROMs/` or `to_compress/`. |
| `compressor.py` | Spawns background subprocesses for `chdman`, `maxcso`, or `dolphintool`. Handles safe deletion of originals on success. |
| `cleaner.py` | Sweeps the directory at the end to remove empty leftover folders. |
| `twoWayDict.py` | Bidirectional dictionary utility used internally. |
| `titles_db.json` | Local hash-to-title database for MD5 verification. |
| `valid_suffix.txt` | Allowlist of valid ROM/disc file extensions. |
| `suffix_sizes.txt` | Size thresholds per extension for heuristic routing. |
| `console_tags_serials.txt` | Serial-number prefix-to-console mapping for deep scanning. |

---

## Prerequisites & Setup

### 1. Python Requirements

Requires **Python 3.8+**. The core pipeline uses only standard library modules:

```
tkinter, pathlib, subprocess, logging, hashlib, re, shutil
```

### 2. Required Data Files

Ensure the following files are in the same directory as `main.py`:

- `valid_suffix.txt`
- `suffix_sizes.txt`
- `console_tags_serials.txt`
- `titles_db.json`

### 3. External Tools

The only tool you need to install manually is **[7-Zip](https://www.7-zip.org/)**, which is used for archive extraction. Install it normally on your system.

All other compression tools (`chdman`, `maxcso`, `DolphinTool`) are downloaded automatically by the script if they are not found in the `tools/` directory. The expected folder layout is:

```
Your_Project_Folder/
 ├── main.py
 ├── gui.py
 ├── processor.py
 ├── ... (other .py and .txt files)
 └── tools/
      ├── chdman.exe          (PS1, PS2, Saturn, SegaCD, Dreamcast)
      ├── maxcso.exe          (PSP)
      └── Dolphin-x64/        (GameCube & Wii)
           ├── DolphinTool.exe
           ├── Qt6Core.dll
           └── Sys/
```

---

## How to Use

### Option A — Run from Source

1. Ensure Python 3.8+ and 7-Zip are installed.
2. Open a terminal in the project folder and run:
   ```bash
   python main.py
   ```

### Option B — Standalone App (`.exe`)

1. Download the latest ZIP from the **[Releases](../../releases)** tab and extract it.
2. Double-click **`ROMOrganizer.exe`** to launch.

### The Organizing Process

1. **Input Directory** — Click *Browse* and select your source folder (e.g., a Downloads folder full of `.zip` files and `.iso` dumps).
2. **Output Directory** — Click *Browse* and select your clean destination (e.g., an external drive or emulator frontend folder). The app creates a `ROMs/` subfolder automatically.
3. **Start** — Click **START ORGANIZING**.
4. **Watch the log** — The live feed shows exactly what the engine is doing: extracting archives, identifying serials, routing files, and running compression.

---

## Supported Compression Formats

| Format | Tool | Systems |
|---|---|---|
| `.chd` | chdman | PS1, PS2, Saturn, SegaCD, Dreamcast |
| `.cso` | maxcso | PSP |
| `.rvz` | DolphinTool | GameCube, Wii |

---

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.

---

## Disclaimer

This tool is intended for use with legally owned ROM backups. The authors do not condone piracy. Always respect the intellectual property rights of game publishers.
