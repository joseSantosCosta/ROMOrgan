import re
from pathlib import Path
import logging
import subprocess
import shutil
import processor


BASE_DIR = Path(__file__).parent.absolute()

CHDMAN_EXE = BASE_DIR / "tools" / "chdman.exe"
MAXCSO_EXE = BASE_DIR / "tools" / "maxcso.exe"
DOLPHIN_EXE = BASE_DIR / "tools" / "Dolphin-x64" / "DolphinTool.exe"

compression_tools_dict = {
    # --- CHDMAN (.chd) ---
    "psx": {"tool": "chdman", "extension": ".chd"},
    "ps2": {"tool": "chdman", "extension": ".chd"},
    "segacd": {"tool": "chdman", "extension": ".chd"},
    "saturn": {"tool": "chdman", "extension": ".chd"},
    "dreamcast": {"tool": "chdman", "extension": ".chd"},
    "tg-cd": {"tool": "chdman", "extension": ".chd"},
    "3do": {"tool": "chdman", "extension": ".chd"},

    # --- DolphinTool (.rvz) ---
    "gc": {"tool": "dolphintool", "extension": ".rvz"},
    "wii": {"tool": "dolphintool", "extension": ".rvz"},

    # --- MaxCSO (.cso) ---
    "psp": {"tool": "maxcso", "extension": ".cso"},
}

REGION_MAP = {
    # --- The Big Three & Global ---
    "USA": "USA",
    "Japan": "Japan",
    "Europe": "Europe",
    "World": "World",

    # --- Combined Regions (Prioritize the primary market) ---
    "USA, Europe": "USA",
    "Japan, USA": "Japan",
    "Japan, Europe": "Japan",
    "USA, Europe, Brazil": "USA",

    # --- Asia & Oceania ---
    "Asia": "Asia",
    "Australia": "Australia",
    "Korea": "Korea",
    "China": "China",
    "Taiwan": "Taiwan",
    "Hong Kong": "Asia",

    # --- Individual European Countries ---
    "France": "Europe",
    "Germany": "Europe",
    "Italy": "Europe",
    "Spain": "Europe",
    "UK": "Europe",
    "Netherlands": "Europe",
    "Sweden": "Europe",
    "Russia": "Europe",
    "Scandinavia": "Europe",

    # --- South America & Others ---
    "Brazil": "Brazil",
    "Canada": "USA", 
    "Latin America": "Latin America"
}

def identify_console(directory: Path, convention_db: dict):
    """
    Identifies a gaming console from a directory name and returns a tuple:
    (Matched Folder String, ES-DE Shortname)
    Example: ("Sony - PlayStation", "psx")
    """
    name_to_esde = {}
    
    for sys_key, values in convention_db.items():
        es_de_name = str(values.get("ES-DE", "")).lower()
        
        variations = [
            sys_key,
            values.get("ES-DE"),
            values.get("Full name"),
            values.get("Manufacture/System"),
            values.get("RetroArch")
        ]
        
        for variant in variations:
            if variant and str(variant).strip():
                name_to_esde[str(variant).lower()] = es_de_name

    if not name_to_esde:
        return None, None

    sorted_names = sorted(name_to_esde.keys(), key=len, reverse=True)
    pattern = re.compile(f"({'|'.join(re.escape(n) for n in sorted_names)})", re.IGNORECASE)
    
    match = pattern.search(directory.name)
    
    if match and match.group(0).strip():
        found_text = match.group(0)
        return found_text, name_to_esde[found_text.lower()]
    
    return None, None


def compressor(adding: bool, convention_db: dict,subfolders:str):
    """
    Scans the 'to_compress' folder, identifies systems, and compresses disc images.
    Auto-detects the user's chosen folder convention by checking existing folders.
    """
    logging.info("Initiating the compressing process")
    input_dir = Path() / 'to_compress'

    if not input_dir.exists():
        logging.error(f"Input directory does not exist: {input_dir.absolute()}")
        return

    for directory in input_dir.glob('*'):
        if not directory.is_dir():
            continue

        match_str, es_de_name = identify_console(directory, convention_db)

        if not es_de_name or es_de_name not in compression_tools_dict:
            continue

        # --- AUTO-DETECT EXISTING CONVENTION ---
        roms_base_dir = Path() if adding else Path() / 'ROMs'
        final_folder_name = es_de_name # Fallback
        
        systems = convention_db.get("systems", convention_db)
        
        for sys_key, values in systems.items():
            if str(values.get("ES-DE", "")).lower() == es_de_name:
                
                variations = [
                    values.get("ES-DE"), 
                    values.get("Full name"), 
                    values.get("Manufacture/System"), 
                    values.get("RetroArch")
                ]
                
                for variant in variations:
                    if variant and (roms_base_dir / str(variant)).exists():
                        final_folder_name = str(variant)
                        break
                break

        tool_config = compression_tools_dict[es_de_name]
        tool = tool_config['tool']
        ext = tool_config['extension']
        
        valid_inputs = ['.cue', '.iso', '.gdi', '.gcm', '.wbfs']

        for game in directory.rglob('*'):
            if not game.is_file() or game.suffix.lower() not in valid_inputs:
                continue

            output_file = game.with_suffix(ext)
            command = None

            if tool == 'chdman':
                command = [str(CHDMAN_EXE), 'createcd', '-i', str(game), '-o', str(output_file)]
            elif tool == 'dolphintool':
                command = [str(DOLPHIN_EXE), 'convert', '-i', str(game), '-o', str(output_file), "-f", "rvz"]
            elif tool == 'maxcso':
                command = [str(MAXCSO_EXE), '--out', str(output_file), str(game)]

            if not command:
                logging.error(f"Command logic for tool '{tool}' is missing.")
                continue

            logging.info(f"Converting {game.name} using {tool}...")
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                logging.info(f"Success! {output_file.name} created.")
                if subfolders == 'Region':
                    region = processor.extract_region(game.name,REGION_MAP)
                    dest_dir = roms_base_dir / final_folder_name / region
                    logging.info(f"Creating {dest_dir.absolute()} to put {output_file}")
                    dest_dir.mkdir(parents=True,exist_ok=True)
                    logging.info(f"Standardized console folder name detected as: {final_folder_name}")
                    logging.info(f"Moving to {dest_dir.absolute()}")
                    shutil.move(output_file, dest_dir)
                elif subfolders == 'Alphabetical':
                    first_letter = game.name[0]
                    dest_dir = roms_base_dir / final_folder_name / first_letter
                    logging.info(f"Creating {dest_dir.absolute()} to put {output_file}")
                    dest_dir.mkdir(parents=True,exist_ok=True)
                    logging.info(f"Moving to {dest_dir.absolute()}")
                    shutil.move(output_file,dest_dir)                
                else:
                    dest_dir = roms_base_dir / final_folder_name
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    logging.info(f"Standardized console folder name detected as: {final_folder_name}")
                    logging.info(f"Moving to {dest_dir.absolute()}")
                    shutil.move(output_file, dest_dir)

                
                try:
                    original_ext = game.suffix.lower()
                    
                    if original_ext == '.cue':
                        with open(game, 'r', encoding='utf-8', errors='ignore') as f:
                            tracks = re.findall(r'"([^"]+)"', f.read())
                            for track in tracks:
                                (game.parent / track).unlink(missing_ok=True)
                    
                    if original_ext in ['.cue', '.gdi']:
                        for assoc in game.parent.glob(f"{game.stem}*"):
                            if assoc.suffix.lower() in ['.cue', '.bin', '.gdi', '.raw']:
                                assoc.unlink(missing_ok=True)

                    game.unlink(missing_ok=True)
                    logging.info(f"Cleaned up source files for {game.name}")

                except Exception as e:
                    logging.error(f"Error handling original files for {game.name}: {e}")
            else:
                logging.error(f"Compression failed for {game.name}. stderr: {result.stderr}")
    




            










