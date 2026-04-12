from pathlib import Path
import shutil
import tempfile
import re
import logging
import json
import hashlib

#This module will receive a dictionary from the classifier.classify_files() function 
BASE_DIR = Path(__file__).parent.absolute()

console_dict = {
    # --- Nintendo ---
    "NES": ("NES", False),
    "SNES": ("SNES", False),
    "N64": ("N64", False),
    "GB": ("Game Boy", False),
    "GBC": ("Game Boy Color", False),
    "GBA": ("Game Boy Advance", False),
    "NDS": ("Nintendo DS", False),
    "3DS": ("Nintendo 3DS", False),
    "VB": ("Virtual Boy", False),
    "POKEMINI": ("Pokemon Mini", False),
    "SWITCH": ("Nintendo Switch", False), # Switch games use XCI/NSP, no need for CHD
    "GC": ("GameCube", True),             # Compresses to .rvz
    "WII": ("Wii", True),                 # Compresses to .rvz
    "WIIU": ("Wii U", True),              # Compresses to .wua

    # --- Sony ---
    "PS1": ("PlayStation 1", True),       # Compresses to .chd
    "PS2": ("PlayStation 2", True),       # Compresses to .chd
    "PS3": ("PlayStation 3", True),       # Can be ISO compressed
    "PS4": ("PlayStation 4", False),      # Uses PKG
    "PSP": ("PSP", True),                 # Compresses to .cso or .chd
    "VITA": ("PS Vita", False),           # Uses VPK/MaiDump

    # --- Sega ---
    "SG1000": ("SG-1000", False),
    "SMS": ("Master System", False),
    "GENESIS": ("Genesis", False),
    "32X": ("32X", False),
    "SegaCD": ("Sega CD", True),          # Compresses to .chd
    "Saturn": ("Saturn", True),           # Compresses to .chd
    "DC": ("Dreamcast", True),            # Compresses to .chd
    "GG": ("Game Gear", False),

    # --- Microsoft ---
    "XBOX": ("Xbox", True),               # Compresses to .ciso or ISO
    "X360": ("Xbox 360", True),           # Uses ISO

    # --- Atari ---
    "A2600": ("Atari 2600", False),
    "A5200": ("Atari 5200", False),
    "A7800": ("Atari 7800", False),
    "LYNX": ("Atari Lynx", False),
    "JAG": ("Atari Jaguar", False),       # Base Jaguar is cart, Jaguar CD would be True

    # --- NEC / TurboGrafx ---
    "PCE": ("PC Engine", False),
    "PCECD": ("PC Engine CD", True),      # Compresses to .chd

    # --- SNK / Neo Geo ---
    "NEOGEO": ("Neo Geo", False),
    "NGP": ("Neo Geo Pocket", False),

    # --- Microcomputers & Others ---
    "3DO": ("3DO", True),                 # Compresses to .chd
    "WS": ("WonderSwan", False),
    "INTV": ("Intellivision", False),
    "COLECO": ("ColecoVision", False),
    "VEC": ("Vectrex", False),
    "AMIGA": ("Commodore Amiga", False),  # Mostly floppies (.adf) or LHA archives
    "C64": ("Commodore 64", False),
    "ZXS": ("ZX Spectrum", False),
    "MSX": ("MSX", False),
    "CPC": ("Amstrad CPC", False),
    "AppleII": ("Apple II", False),
}

extension_map = {
    # --- A ---
    ".a26": ["A2600"],         # Atari 2600
    ".a52": ["A5200"],         # Atari 5200
    ".a78": ["A7800"],         # Atari 7800
    ".adf": ["AMIGA"],         # Amiga Disk File
    ".app": ["WIIU"],          # Wii U

    # --- B ---
    ".bin": ["PS1", "PS2", "Saturn", "SegaCD", "GENESIS", "A2600", "PCECD", "INTV"], 
    
    # --- C ---
    ".ccd": ["PS1", "Saturn"], # CloneCD (Often paired with .img/.sub)
    ".cdi": ["DC"],            # Dreamcast (DiscJuggler)
    ".cdt": ["CPC"],           # Amstrad CPC Tape
    ".chd": ["PS1", "PS2", "Saturn", "SegaCD", "DC", "PCECD", "3DO"], # Compressed Hunks of Data
    ".cia": ["3DS"],           # Nintendo 3DS
    ".ciso": ["GC", "WII"],    # Compact ISO
    ".col": ["COLECO"],        # ColecoVision
    ".crt": ["C64"],           # Commodore 64 Cartridge
    ".cso": ["PSP"],           # Compressed ISO
    ".cue": ["PS1", "Saturn", "SegaCD", "PCECD", "3DO"], # Cue sheet for optical media
    ".cxi": ["3DS"],           # 3DS executable

    # --- D ---
    ".d64": ["C64"],           # Commodore 64 Disk
    ".dsi": ["NDS"],           # Nintendo DSi
    ".dsk": ["CPC", "MSX", "AppleII"], # Generic Disk image

    # --- F ---
    ".fds": ["NES"],           # Famicom Disk System
    ".fig": ["SNES"],          # Super Famicom

    # --- G ---
    ".gb": ["GB"],             # Game Boy
    ".gba": ["GBA"],           # Game Boy Advance
    ".gbc": ["GBC"],           # Game Boy Color
    ".gcm": ["GC"],            # GameCube Master
    ".gdi": ["DC"],            # Dreamcast (Gigabyte Disc)
    ".gen": ["GENESIS"],       # Sega Genesis
    ".gg": ["GG"],             # Sega Game Gear

    # --- H ---
    ".hdf": ["AMIGA"],         # Amiga Hard Disk

    # --- I ---
    ".img": ["PS1", "PS2"],    # CloneCD Image or generic floppy
    ".int": ["INTV"],          # Intellivision
    ".ipf": ["AMIGA"],         # Amiga Interchange Format
    ".iso": ["PS1", "PS2", "PS3", "PSP", "GC", "WII", "Saturn", "XBOX", "X360"],

    # --- J ---
    ".j64": ["JAG"],           # Atari Jaguar
    ".jag": ["JAG"],           # Atari Jaguar

    # --- L ---
    ".lnx": ["LYNX"],          # Atari Lynx

    # --- M ---
    ".m3u": ["PS1", "Saturn", "SegaCD", "DC"], # Playlist file for multi-disc games
    ".mai": ["VITA"],          # PS Vita MaiDump
    ".md": ["GENESIS"],        # Sega Mega Drive
    ".mdf": ["PS1", "PS2"],    # Alcohol 120% Image
    ".mds": ["PS1", "PS2"],    # Alcohol 120% Info
    ".min": ["POKEMINI"],      # Pokemon Mini

    # --- N ---
    ".n64": ["N64"],           # Nintendo 64
    ".nca": ["SWITCH"],        # Nintendo Switch
    ".ndd": ["N64"],           # Nintendo 64DD
    ".nds": ["NDS"],           # Nintendo DS
    ".neo": ["NEOGEO"],        # Neo Geo
    ".nes": ["NES"],           # Nintendo Entertainment System
    ".ngc": ["NGP"],           # Neo Geo Pocket Color
    ".ngp": ["NGP"],           # Neo Geo Pocket
    ".nsp": ["SWITCH"],        # Nintendo Switch Package

    # --- P ---
    ".pbp": ["PS1", "PSP"],    # PlayStation Portable Eboot
    ".pce": ["PCE"],           # TurboGrafx-16 / PC Engine
    ".pkg": ["PS3", "VITA"],   # PlayStation Package
    ".prg": ["C64"],           # Commodore 64 Program
    ".pup": ["PS3", "PS4"],    # PlayStation Update File

    # --- R ---
    ".rvz": ["GC", "WII"],     # Dolphin Emulator Compressed Image

    # --- S ---
    ".sbi": ["PS1"],           # PS1 Subchannel Data (European games)
    ".sfc": ["SNES"],          # Super Famicom
    ".sg": ["SMS"],            # SG-1000
    ".sgb": ["GB"],            # Super Game Boy
    ".smc": ["SNES"],          # Super Magic Drive (SNES)
    ".smd": ["GENESIS"],       # Super Magic Drive (Genesis)
    ".sms": ["SMS"],           # Sega Master System
    ".sna": ["ZXS"],           # ZX Spectrum Snapshot
    ".sub": ["PS1", "Saturn"], # CloneCD Subchannel data
    ".swc": ["SNES"],          # Super Wild Card (SNES)

    # --- T ---
    ".t64": ["C64"],           # Commodore 64 Tape
    ".tap": ["C64", "ZXS"],    # Tape Image
    ".toc": ["PS1", "Saturn"], # Table of Contents (usually with .bin)
    ".tzx": ["ZXS"],           # ZX Spectrum Tape

    # --- U ---
    ".unf": ["NES"],           # UNIF NES ROM

    # --- V ---
    ".v64": ["N64"],           # Nintendo 64 (Doctor V64)
    ".vb": ["VB"],             # Virtual Boy
    ".vec": ["VEC"],           # Vectrex
    ".vpk": ["VITA"],          # PS Vita Package

    # --- W ---
    ".wad": ["WII"],           # Wii Channel File
    ".wbfs": ["WII"],          # Wii Backup File System
    ".ws": ["WS"],             # WonderSwan
    ".wsc": ["WS"],            # WonderSwan Color
    ".wua": ["WIIU"],          # Wii U Archive
    ".wud": ["WIIU"],          # Wii U Disc Image
    ".wux": ["WIIU"],          # Wii U Compressed Disc Image

    # --- X ---
    ".xci": ["SWITCH"],        # Switch Cartridge Image
    ".xiso": ["XBOX"],         # Xbox ISO

    # --- Z ---
    ".z64": ["N64"],           # Nintendo 64 (Z64 format)
    ".z80": ["ZXS"],           # ZX Spectrum Z80 Snapshot
    ".zso": ["PSP", "PS2"],    # Zstandard Compressed ISO
}

#file=Path(r'd:/file.jpg').stat().st_size -> get the size of a file

def create_folders() -> None:
    """
    This function will create the ROMs folder and the to_compress folder by looking at the console dict in order to see which consoles
    might have games that can be compressed and whichs don't

    It will also create the subfolder for each console in both ROMs and to_compress folder

    This is a helper function for the processor function

    this function doesn't return anything
    """
    logging.debug("Creating ROMs folder...")
    ROMs_folder = Path() / "ROMs"
    ROMs_folder.mkdir(exist_ok=True)
    
    logging.debug("Creating to_compress folder...")
    to_compress_folder = Path() / "to_compress"
    to_compress_folder.mkdir(exist_ok=True)
    
    logging.debug("Creating unknown folder")
    unknown_folder = Path() / "unknown"
    unknown_folder.mkdir(exist_ok=True)
    
    logging.debug("Creating ambiguous folder")
    ambiguous_folder = Path() / "ambiguous"
    ambiguous_folder.mkdir(exist_ok=True)

    logging.debug("Creating ambiguous_to_compress folder")
    ambiguous_to_compress_folder = Path() / "ambiguous_to_compress"
    ambiguous_to_compress_folder.mkdir(exist_ok=True)

    for console,dir_flag in console_dict.items():
        logging.debug(f"Creating ROMs/{console} subfolder")
        dest = Path() / "ROMs" / f"{console}"
        dest.mkdir(exist_ok=True)
        if dir_flag[1] == True:
            logging.debug(f"Creating to_compress/{console} folder")
            dest = Path() / "to_compress" / f"{console}_to_compress"
            dest.mkdir(exist_ok=True)

def normalize_file_name(file: Path) -> str:
    """
    Removes the extension, removes region tags in () or [], 
    and removes special characters.
    """
    file_name = file.stem.lower() 
    file_name = re.sub(r'\(.*?\)|\[.*?\]', '', file_name)
    clean_file_name = re.sub(r'[^a-zA-Z0-9-\s]', ' ', file_name)
    return " ".join(clean_file_name.split())

def md5_file(filepath:Path):

    md5 = hashlib.md5()
    
    with open(filepath, "rb") as f: 
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    
    return md5.hexdigest()

def deep_serial_scanner(filepath: Path, tied_consoles: list) -> str:
    """
    Reads the first 2MB of an ISO to find hidden internal serial numbers.
    Returns the console name if a match is found, otherwise returns None.
    """
    try:
        with open(filepath, "rb") as f:
            raw_bytes = f.read(2 * 1024 * 1024) 
            
        header_text = raw_bytes.decode('ascii', errors='ignore')
        
        sony_match = re.search(r'([A-Z]{4})[-_]?(\d{5})', header_text)
        if sony_match:
            prefix = sony_match.group(1).lower() # e.g., 'ulus'
            if prefix in ['ulus', 'ules', 'ucus', 'uces', 'npjh', 'npuh'] and 'PSP' in tied_consoles:
                return 'PSP'
            if prefix in ['slus', 'sles', 'scus', 'sces', 'slpm'] and 'PS2' in tied_consoles:
                return 'PS2'
            if prefix in ['slps'] and 'PS1' in tied_consoles:
                return 'PS1'

        nintendo_match = re.search(r'([A-Z0-9]{4}[EJPX][A-Z0-9])\s*Nintendo', header_text, re.IGNORECASE)
        if nintendo_match:
            code = nintendo_match.group(1)
            # Wii games usually start with R, S, or H
            if code.startswith(('R', 'S', 'H')) and 'WII' in tied_consoles:
                return 'WII'
            # GameCube games usually start with G
            if code.startswith('G') and 'GC' in tied_consoles:
                return 'GC'

    except Exception as e:
        logging.error(f"Deep scan failed for {filepath.name}: {e}")
        
    return None

def size_name_serial_heuristic(file:Path, size_dict:dict, console_tag_serial:dict) -> str:
    """Needs doc"""
    candidates = extension_map[file.suffix] if file.suffix in extension_map else []
    
    console_score = {key : 0 for key in candidates}

    suffix:str = file.suffix
    size_of_file:float = file.stat().st_size / (1024**2) # Size in megabytes
    
    for ext_console, sizes in size_dict.items():
        console_name = ext_console[1] # e.g., 'PS1'
        optimal_min = float(sizes[0]) + 100
        optimal_max = float(sizes[1]) - 100
        
        if ext_console[0] == suffix and console_name in console_score:
            
            if float(sizes[0]) <= size_of_file <= float(sizes[1]):
                console_score[console_name] += 3
                logging.debug(f"{file.name} fits the size criteria of {console_name}: +3")
                
                if optimal_min <= size_of_file <= optimal_max and (float(sizes[1]) - float(sizes[0]) >= 300):
                    console_score[console_name] += 4
                    logging.debug(f"{file.name} fits the size criteria of {console_name} in an optimal range: +4")
            else:
                console_score[console_name] -= 1
                logging.debug(f"{file.name} its outside of the {console_name} file range : -1")


    normalized_file_name = normalize_file_name(file)
    file_name_tokens = normalized_file_name.split()
    extract_serial = re.search(r"([a-z]{4})[-._]?(\d{5})", normalized_file_name)
    extracted_serial = None
    if extract_serial:
        extracted_serial = f"{extract_serial.group(1)}-{extract_serial.group(2)}".lower()
    

    # Score by name
    for match in candidates:
        tags = [t.lower() for t in console_tag_serial[match][0]]
        serials = [s.lower() for s in console_tag_serial[match][1]]
        
        tokens_in_tag = list(filter(lambda x : x in tags, file_name_tokens))
        console_score[match] += len(tokens_in_tag) 

        # Score by serial
        if extracted_serial:
            serial_hits = list(filter(lambda p: extracted_serial.startswith(p), serials))
            if serial_hits:
                console_score[match] += 10
                logging.debug(f"The serial number of {file.name} matches the one of {match} +10")
    
    if candidates == []:
        logging.debug("There were no candidates so returning unknown")
        return 'unknown'
    
    max_val = max(console_score.values())

    if max_val == 0:
        logging.debug(f"Could not decide a path for {file.name}")
        return 'ambiguous'
        
    keys_max = [key for key, score in console_score.items() if score == max_val]
    
    if len(keys_max) == 1:
        logging.debug(f"Heuristic winner determined: {keys_max[0]} (Score: {max_val})")
        return keys_max[0]
    else:
        db_path = BASE_DIR / 'titles_db.json'
        with open(db_path, 'r', encoding='utf-8') as f:
            titles = json.load(f)
            json_candidates = [key for key in keys_max if normalized_file_name in titles.get(key, {})]
            
            if len(json_candidates) == 1:
                return json_candidates[0]
                
            elif len(json_candidates) > 1: 
                md5 = md5_file(file)
                for candidate in json_candidates:
                    if md5 in titles[candidate][normalized_file_name]:
                        return candidate
                logging.info(f"Hash mismatch for {file.name}. Running Deep Serial Scan...")
                deep_match = deep_serial_scanner(file, json_candidates)
                if deep_match:
                    logging.info(f"Deep Scan found internal serial! Assigned to {deep_match}")
                    return deep_match

            # If ALL of that fails, we truly give up.
            logging.debug(f"Tie remains or no match found for {file.name}. Returning 'ambiguous'.")
            return 'ambiguous'

            

def resolve_console(file:Path,suffix_size_dict,console_tag_serial:dict) -> str:
    """Needs doc"""
    suffix = file.suffix
    if suffix not in extension_map:
        logging.debug(f"{file.name} assigned unkown")
        return 'unknown'
    elif len(extension_map[suffix]) == 1:
        logging.debug(f"{file.name} assigned {extension_map[suffix][0]}")
        return extension_map[suffix][0]
    elif len(extension_map[suffix]) > 1:
        result = size_name_serial_heuristic(file,suffix_size_dict,console_tag_serial)
        logging.debug(f"{file.name} assigned to {result}")
        return result
        


def get_destination(console, to_compress=False):
    """Needs doc"""
    if console in ('unknown', None):
        return Path() / 'unknown'

    if console == 'ambiguous':
        return Path() / ('ambiguous_to_compress' if to_compress else 'ambiguous')

    if to_compress:
        return Path() / 'to_compress' / f"{console}_to_compress"

    return Path() / 'ROMs' / console


def processor(file_types: dict, tempDir: tempfile,suffix_size_dict:dict,console_tag_serial:dict):
    """
    This function receives a dictionary for the type of file, a temporary Directory and a dictionary with the file sizes of each extension
    console combination
    
    It will move each file to the corresponding console directory, games that need to be extract will go to the "to_compress"
    before being moved to the final console directory

    The folder are created using the create_folders function

    This function will also delete the temporary directory used to store the extracted game files
    """    

    with tempDir as tempDir:

        for type, files in file_types.items():
            if type == 'to_compress' or type == 'not_to_compress':
                logging.debug("Moving files...")
                for file in files:
                    console= resolve_console(file,suffix_size_dict,console_tag_serial)
                    if type == 'to_compress':
                        dest = get_destination(console,to_compress=True)
                        dest.mkdir(parents=True,exist_ok=True)
                        if file.exists():
                            shutil.move(file,dest)
                            logging.debug(f"Moved {file.name} to {dest.name}")
                    elif type == 'not_to_compress':
                        dest = get_destination(console,to_compress=False)
                        dest.mkdir(parents=True,exist_ok=True)
                        if file.exists():
                            shutil.move(file,dest)
                            logging.debug(f"Moved {file.name} to {dest.name}")
            else:
                continue
                
    

                    




    


        
            

        


            
        
    

    

