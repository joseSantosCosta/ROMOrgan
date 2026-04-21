# ROMOrgan

> **Work in Progress** — This project is actively under development. Features may be incomplete, change without notice, or behave unexpectedly. Contributions and feedback are welcome.

An automated, intelligent Python pipeline with a native GUI designed to sort, extract, verify, and compress retro video game ROMs and disc images.

Instead of manually sorting through terabytes of messy `.zip`, `.7z`, `.bin/.cue`, and `.iso` files, ROMOrgan uses a custom heuristic engine, database hash-matching, and deep boot-sector scanning to identify games, move them to the correct console folders, and automatically compress them into modern formats (`.chd`, `.cso`, `.rvz`) to save storage space.

---

## How It Works

ROMOrgan runs your files through a multi-stage pipeline. The `classifier` first determines whether each file is a ROM, an archive to be extracted, or junk. Archives are unpacked into a temporary workspace and re-classified. The `processor` then identifies each game through a combination of file extension heuristics, deep serial scanning (reading the first 2MB of disc images to find internal codes like `SLUS-20001`), and MD5 hash matching against a local database. Once identified, files are moved to the correct console folder and optionally compressed using external tools (`chdman`, `maxcso`, `dolphintool`). A final cleanup pass removes any empty leftover folders.

The pipeline is exposed through a native Tkinter GUI that lets you select input and output folders and watch a live log feed without the interface freezing.

---

## Project Structure

| File | Role |
|---|---|
| `main.py` | Entry point. Houses the GUI and orchestrates the full pipeline |
| `rules.py` | Loads extension, size, and console tag dictionaries from `.txt` files |
| `scanner.py` | Crawls the input directory to find all available files |
| `classifier.py` | Determines if a file is a ROM, an archive, or trash |
| `extractor.py` | Safely extracts archives into a temp directory for re-classification |
| `processor.py` | Runs the Heuristic Engine, Serial Scanner, and Hash Matcher. Moves files to destination |
| `compressor.py` | Spawns subprocesses to run `chdman`, `maxcso`, or `dolphintool` |
| `cleaner.py` | Sweeps leftover empty folders at the end of the process |

---

## Prerequisites & Setup

ROMOrgan requires **Python 3.8+** and uses only standard library modules, so no heavy dependencies are needed. The following rule files must be present in the same directory as `main.py`: `valid_suffix.txt`, `suffix_sizes.txt`, `console_tags_serials.txt`, and `titles_db.json`.

For compression to work, external tools must be placed inside a `tools/` folder next to `main.py`:

```
Your_Project_Folder/
 ├── main.py
 ├── processor.py
 ├── ... (other .py and .txt files)
 └── tools/
      ├── chdman.exe
      ├── maxcso.exe
      └── Dolphin-x64/
           ├── DolphinTool.exe
           ├── Qt6Core.dll
           └── Sys/
```

Due to licensing, these tools are not bundled and must be downloaded separately. You will need [7-Zip](https://www.7-zip.org/) installed on your system, [UnRAR for Windows](https://www.rarlab.com/rar_add.htm) (`UnRar.exe` placed in `tools/`) for `.rar` support, [CHDMAN](https://www.mamedev.org/release.html) from the MAME release, [MaxCSO](https://github.com/unknownbrackets/maxcso/releases), and the [Dolphin Emulator](https://dolphin-emu.org/download/) x64 build with its folder renamed to `Dolphin-x64`.

---

## How to Use

Download the latest ZIP from the [Releases](https://github.com/joseSantosCosta/ROMOrgan/releases) tab, extract it, place the external tools in the `tools/` folder, and run `ROMOrganizer.exe`. To run from source, simply execute `python main.py`.

Once the application is open, select your input directory (the messy folder with your unorganized ROMs) and your output directory (ROMOrgan will create a `ROMs/` subfolder inside it automatically). Click **START ORGANIZING** and watch the live log.

---

## Supported Output Conventions

ROMOrgan can organize your library following the most common emulation frontend conventions. The default is ES-DE (e.g. `roms/gba/`), with additional support for full system names (`roms/Game Boy Advance/`), manufacturer/system hierarchy (`roms/Nintendo/Game Boy Advance/`), and the Libretro format (`roms/Nintendo - Game Boy Advance/`).

---

## Roadmap

- [x] Heuristic engine for ROM identification
- [x] Deep serial scanning for disc-based games
- [x] Hash-based verification via local database
- [x] Automated compression (CHD, CSO, RVZ)
- [ ] Existing library detection and convention matching
- [ ] Region subfolder support (US, Japan, Europe, Translated, Hacks)
- [ ] Alphabetical subfolder support for large libraries
- [ ] Cross-platform support (Linux, macOS)

---

## Supported Systems

ROMOrgan currently supports identification and organization for consoles from Nintendo (NES, SNES, N64, Game Boy, Game Boy Color, Game Boy Advance, Nintendo DS, Nintendo 3DS, Virtual Boy, Pokemon Mini, GameCube, Wii, Wii U, Nintendo Switch), Sony (PlayStation 1–4, PSP, PS Vita), Sega (SG-1000, Master System, Genesis/Mega Drive, 32X, Sega CD, Saturn, Dreamcast, Game Gear), Microsoft (Xbox, Xbox 360), Atari (2600, 5200, 7800, Lynx, Jaguar), NEC (PC Engine/TurboGrafx-16, PC Engine CD), SNK (Neo Geo, Neo Geo Pocket), and others including 3DO, WonderSwan, Intellivision, ColecoVision, Vectrex, Commodore Amiga, Commodore 64, ZX Spectrum, MSX, Amstrad CPC, and Apple II.

---

## Contributing

This project is in active development and contributions are very welcome. Feel free to open an issue or submit a pull request.

---

## License

This project is open source. See the [LICENSE](LICENSE) file for details.
