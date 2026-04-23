from pathlib import Path
import shutil
import tempfile
import re
import logging
import json
import hashlib
from twoWayDict import twoWayDict
import rename
import os
#This module will receive a dictionary from the classifier.classify_files() function 
BASE_DIR = Path(__file__).parent.absolute()

console_dict = {
    # --- Nintendo ---
    "nes": ("nes", False),
    "snes": ("snes", False),
    "n64": ("n64", False),
    "gb": ("gb", False),
    "gbc": ("gbc", False),
    "gba": ("gba", False),
    "nds": ("nds", False),
    "3ds": ("3ds", False),
    "virtualboy": ("virtualboy", False),
    "pokemini": ("pokemini", False),
    "switch": ("switch", False),
    "gc": ("gc", True),
    "wii": ("wii", True),
    "wiiu": ("wiiu", True),

    # --- Sony ---
    "psx": ("psx", True),
    "ps2": ("ps2", True),
    "ps3": ("ps3", True),
    "ps4": ("ps4", False),
    "psp": ("psp", True),
    "psvita": ("psvita", False),

    # --- Sega ---
    "sg1000": ("sg1000", False),
    "mastersystem": ("mastersystem", False),
    "megadrive": ("megadrive", False),
    "sega32x": ("sega32x", False),
    "segacd": ("segacd", True),
    "saturn": ("saturn", True),
    "dreamcast": ("dreamcast", True),
    "gamegear": ("gamegear", False),

    # --- Microsoft ---
    "xbox": ("xbox", True),
    "xbox360": ("xbox360", True),

    # --- Atari ---
    "atari2600": ("atari2600", False),
    "atari5200": ("atari5200", False),
    "atari7800": ("atari7800", False),
    "atarilynx": ("atarilynx", False),
    "atarijaguar": ("atarijaguar", False),

    # --- NEC / TurboGrafx ---
    "tg16": ("tg16", False),
    "tg-cd": ("tg-cd", True),

    # --- SNK / Neo Geo ---
    "neogeo": ("neogeo", False),
    "ngp": ("ngp", False),

    # --- Microcomputers & Others ---
    "3do": ("3do", True),
    "wonderswan": ("wonderswan", False),
    "intellivision": ("intellivision", False),
    "colecovision": ("colecovision", False),
    "vectrex": ("vectrex", False),
    "amiga": ("amiga", False),
    "c64": ("c64", False),
    "zxspectrum": ("zxspectrum", False),
    "msx": ("msx", False),
    "amstradcpc": ("amstradcpc", False),
    "apple2": ("apple2", False),
}

extension_map = {
    # --- A ---
    ".a26": ["atari2600"],         # Atari 2600
    ".a52": ["atari5200"],         # Atari 5200
    ".a78": ["atari7800"],         # Atari 7800
    ".adf": ["amiga"],             # Amiga Disk File
    ".app": ["wiiu"],              # Wii U

    # --- B ---
    ".bin": ["psx", "ps2", "saturn", "segacd", "megadrive", "atari2600", "tg-cd", "intellivision"], 
    
    # --- C ---
    ".ccd": ["psx", "saturn"],     # CloneCD (Often paired with .img/.sub)
    ".cdi": ["dreamcast"],         # Dreamcast (DiscJuggler)
    ".cdt": ["amstradcpc"],        # Amstrad CPC Tape
    ".chd": ["psx", "ps2", "saturn", "segacd", "dreamcast", "tg-cd", "3do"], # Compressed Hunks of Data
    ".cia": ["3ds"],               # Nintendo 3DS
    ".ciso": ["gc", "wii"],        # Compact ISO
    ".col": ["colecovision"],      # ColecoVision
    ".crt": ["c64"],               # Commodore 64 Cartridge
    ".cso": ["psp"],               # Compressed ISO
    ".cue": ["psx", "saturn", "segacd", "tg-cd", "3do"], # Cue sheet for optical media
    ".cxi": ["3ds"],               # 3DS executable

    # --- D ---
    ".d64": ["c64"],               # Commodore 64 Disk
    ".dsi": ["nds"],               # Nintendo DSi
    ".dsk": ["amstradcpc", "msx", "apple2"], # Generic Disk image

    # --- F ---
    ".fds": ["nes"],               # Famicom Disk System
    ".fig": ["snes"],              # Super Famicom

    # --- G ---
    ".gb": ["gb"],                 # Game Boy
    ".gba": ["gba"],               # Game Boy Advance
    ".gbc": ["gbc"],               # Game Boy Color
    ".gcm": ["gc"],                # GameCube Master
    ".gdi": ["dreamcast"],         # Dreamcast (Gigabyte Disc)
    ".gen": ["megadrive"],         # Sega Genesis
    ".gg": ["gamegear"],           # Sega Game Gear

    # --- H ---
    ".hdf": ["amiga"],             # Amiga Hard Disk

    # --- I ---
    ".img": ["psx", "ps2"],        # CloneCD Image or generic floppy
    ".int": ["intellivision"],     # Intellivision
    ".ipf": ["amiga"],             # Amiga Interchange Format
    ".iso": ["psx", "ps2", "ps3", "psp", "gc", "wii", "saturn", "xbox", "xbox360"],

    # --- J ---
    ".j64": ["atarijaguar"],       # Atari Jaguar
    ".jag": ["atarijaguar"],       # Atari Jaguar

    # --- L ---
    ".lnx": ["atarilynx"],         # Atari Lynx

    # --- M ---
    ".m3u": ["psx", "saturn", "segacd", "dreamcast"], # Playlist file for multi-disc games
    ".mai": ["psvita"],            # PS Vita MaiDump
    ".md": ["megadrive"],          # Sega Mega Drive
    ".mdf": ["psx", "ps2"],        # Alcohol 120% Image
    ".mds": ["psx", "ps2"],        # Alcohol 120% Info
    ".min": ["pokemini"],          # Pokemon Mini

    # --- N ---
    ".n64": ["n64"],               # Nintendo 64
    ".nca": ["switch"],            # Nintendo Switch
    ".ndd": ["n64"],               # Nintendo 64DD
    ".nds": ["nds"],               # Nintendo DS
    ".neo": ["neogeo"],            # Neo Geo
    ".nes": ["nes"],               # Nintendo Entertainment System
    ".ngc": ["ngpc"],              # Neo Geo Pocket Color
    ".ngp": ["ngp"],               # Neo Geo Pocket
    ".nsp": ["switch"],            # Nintendo Switch Package

    # --- P ---
    ".pbp": ["psx", "psp"],        # PlayStation Portable Eboot
    ".pce": ["tg16"],              # TurboGrafx-16 / PC Engine
    ".pkg": ["ps3", "psvita"],     # PlayStation Package
    ".prg": ["c64"],               # Commodore 64 Program
    ".pup": ["ps3", "ps4"],        # PlayStation Update File

    # --- R ---
    ".rvz": ["gc", "wii"],         # Dolphin Emulator Compressed Image

    # --- S ---
    ".sbi": ["psx"],               # PS1 Subchannel Data (European games)
    ".sfc": ["snes"],              # Super Famicom
    ".sg": ["sg1000"],             # SG-1000
    ".sgb": ["gb"],                # Super Game Boy
    ".smc": ["snes"],              # Super Magic Drive (SNES)
    ".smd": ["megadrive"],         # Super Magic Drive (Genesis)
    ".sms": ["mastersystem"],      # Sega Master System
    ".sna": ["zxspectrum"],        # ZX Spectrum Snapshot
    ".sub": ["psx", "saturn"],     # CloneCD Subchannel data
    ".swc": ["snes"],              # Super Wild Card (SNES)

    # --- T ---
    ".t64": ["c64"],               # Commodore 64 Tape
    ".tap": ["c64", "zxspectrum"], # Tape Image
    ".toc": ["psx", "saturn"],     # Table of Contents (usually with .bin)
    ".tzx": ["zxspectrum"],        # ZX Spectrum Tape

    # --- U ---
    ".unf": ["nes"],               # UNIF NES ROM

    # --- V ---
    ".v64": ["n64"],               # Nintendo 64 (Doctor V64)
    ".vb": ["virtualboy"],         # Virtual Boy
    ".vec": ["vectrex"],           # Vectrex
    ".vpk": ["psvita"],            # PS Vita Package

    # --- W ---
    ".wad": ["wii"],               # Wii Channel File
    ".wbfs": ["wii"],              # Wii Backup File System
    ".ws": ["wonderswan"],         # WonderSwan
    ".wsc": ["wonderswancolor"],   # WonderSwan Color
    ".wua": ["wiiu"],              # Wii U Archive
    ".wud": ["wiiu"],              # Wii U Disc Image
    ".wux": ["wiiu"],              # Wii U Compressed Disc Image

    # --- X ---
    ".xci": ["switch"],            # Switch Cartridge Image
    ".xiso": ["xbox"],             # Xbox ISO

    # --- Z ---
    ".z64": ["n64"],               # Nintendo 64 (Z64 format)
    ".z80": ["zxspectrum"],        # ZX Spectrum Z80 Snapshot
    ".zso": ["psp", "ps2"],        # Zstandard Compressed ISO
}

# Format: "INTERNAL_TAG": ["Alias 1", "Alias 2"]
CONSOLE_ALIASES = {
    # --- Nintendo ---
    "nes": ["NES", "Nintendo Entertainment System", "Famicom", "Nintendo"],
    "snes": ["SNES", "Super Nintendo", "Super Famicom", "Super Nintendo Entertainment System", "SFC"],
    "n64": ["N64", "Nintendo 64"],
    "gb": ["GB", "Game Boy", "Gameboy", "Nintendo Game Boy"],
    "gbc": ["GBC", "Game Boy Color", "Gameboy Color"],
    "gba": ["GBA", "Game Boy Advance", "Gameboy Advance"],
    "nds": ["NDS", "DS", "Nintendo DS"],
    "3ds": ["3DS", "Nintendo 3DS"],
    "virtualboy": ["VB", "Virtual Boy", "Nintendo Virtual Boy"],
    "pokemini": ["Pokemon Mini", "PokeMini"],
    "switch": ["SWITCH", "Nintendo Switch", "NS"],
    "gc": ["GC", "GameCube", "Game Cube", "Nintendo GameCube", "GCN"],
    "wii": ["WII", "Wii", "Nintendo Wii"],
    "wiiu": ["WIIU", "Wii U", "Nintendo Wii U"],

    # --- Sony ---
    "psx": ["PS1", "PSX", "PlayStation", "PlayStation 1", "Sony PlayStation"],
    "ps2": ["PS2", "PlayStation 2", "Sony PlayStation 2"],
    "ps3": ["PS3", "PlayStation 3", "Sony PlayStation 3"],
    "ps4": ["PS4", "PlayStation 4", "Sony PlayStation 4"],
    "psp": ["PSP", "PlayStation Portable", "Sony PSP"],
    "psvita": ["VITA", "PS Vita", "PlayStation Vita", "PSVita"],

    # --- Sega ---
    "sg1000": ["SG1000", "SG-1000", "Sega SG-1000"],
    "mastersystem": ["SMS", "Master System", "Sega Master System"],
    "megadrive": ["GENESIS", "Mega Drive", "Sega Genesis", "Sega Mega Drive", "Megadrive"],
    "sega32x": ["32X", "Sega 32X", "Sega Genesis 32X"],
    "segacd": ["SegaCD", "Sega CD", "Mega CD", "Sega Mega-CD"],
    "saturn": ["Saturn", "Sega Saturn"],
    "dreamcast": ["DC", "Dreamcast", "Sega Dreamcast"],
    "gamegear": ["GG", "Game Gear", "Sega Game Gear"],

    # --- Microsoft ---
    "xbox": ["XBOX", "Xbox", "Microsoft Xbox", "Original Xbox"],
    "xbox360": ["X360", "Xbox 360", "Microsoft Xbox 360"],

    # --- Atari ---
    "atari2600": ["A2600", "Atari 2600", "VCS"],
    "atari5200": ["A5200", "Atari 5200"],
    "atari7800": ["A7800", "Atari 7800"],
    "atarilynx": ["LYNX", "Atari Lynx", "Lynx"],
    "atarijaguar": ["JAG", "Atari Jaguar", "Jaguar"],

    # --- NEC / TurboGrafx ---
    "tg16": ["PCE", "PC Engine", "TurboGrafx-16", "TG16", "TurboGrafx"],
    "tg-cd": ["PCECD", "PC Engine CD", "TurboGrafx-CD", "TGCD", "TurboGrafx CD"],

    # --- SNK / Neo Geo ---
    "neogeo": ["NEOGEO", "Neo Geo", "Neo-Geo MVS", "Neo-Geo AES", "NeoGeo AES"],
    "ngp": ["NGP", "Neo Geo Pocket", "NGPC", "Neo Geo Pocket Color"],

    # --- Microcomputers & Others ---
    "3do": ["3DO", "Panasonic 3DO", "3DO Interactive Multiplayer"],
    "wonderswan": ["WS", "WonderSwan", "Bandai WonderSwan", "WSC", "WonderSwan Color"],
    "intellivision": ["INTV", "Intellivision", "Mattel Intellivision"],
    "colecovision": ["COLECO", "ColecoVision", "Coleco"],
    "vectrex": ["VEC", "Vectrex"],
    "amiga": ["AMIGA", "Commodore Amiga", "Amiga 500"],
    "c64": ["C64", "Commodore 64", "C-64"],
    "zxspectrum": ["ZXS", "ZX Spectrum", "Sinclair ZX Spectrum"],
    "msx": ["MSX", "Microsoft MSX"],
    "amstradcpc": ["CPC", "Amstrad CPC"],
    "apple2": ["AppleII", "Apple II", "Apple 2"],
}

console_aliases = twoWayDict(CONSOLE_ALIASES) #this dictionary works both ways



def check_existing_directories(roms_dir:Path)->list:
    """
    It will scan all the directories inside the directory given (ideally it would be the user ROMs directory)

    Returns a list of directories that already exists in the user library
    """
    logging.info("Checking the console folder you already have...")
    new_to_old:dict = rename.change_dir_name(roms_dir)
    already_existing_dir = [folder.name for folder in roms_dir.glob('*') if folder.is_dir()]
    rename.original_dir_name(roms_dir,new_to_old)
    return already_existing_dir
     

def create_folders(create_from_scratch:bool,adding:bool,output_dir:Path) -> None: #this will create folders if the user is creating his first library
    """
    This function will create the ROMs folder and the to_compress folder by looking at the console dict in order to see which consoles
    might have games that can be compressed and whichs don't

    It will also create the subfolder for each console in both ROMs and to_compress folder

    This is a helper function for the processor function

    this function doesn't return anything
    """
    if create_from_scratch:
        logging.info("Creating the library from scratch")
        logging.debug("Creating ROMs folder...")
        ROMs_folder = output_dir / "ROMs"
        ROMs_folder.mkdir(exist_ok=True)
    
        logging.info("Creating to_compress folder...")
        to_compress_folder = output_dir / "to_compress"
        to_compress_folder.mkdir(exist_ok=True)
    
        logging.info("Creating unknown folder")
        unknown_folder = output_dir / "unknown"
        unknown_folder.mkdir(exist_ok=True)
    
        logging.info("Creating ambiguous folder")
        ambiguous_folder = output_dir / "ambiguous"
        ambiguous_folder.mkdir(exist_ok=True)

        logging.info("Creating ambiguous_to_compress folder")
        ambiguous_to_compress_folder = output_dir / "ambiguous_to_compress"
        ambiguous_to_compress_folder.mkdir(exist_ok=True)

        #if convention[0] == 'ES-DE':
        #   convention_manager.create_folders_ESDE(output_dir)

        for console,dir_flag in console_dict.items():
            logging.info(f"Creating ROMs/{console} subfolder")
            dest = output_dir / "ROMs" / f"{console}"
            dest.mkdir(exist_ok=True)
            if dir_flag[1] == True:
                logging.info(f"Creating to_compress/{console} folder")
                dest = output_dir / "to_compress" / f"{console}_to_compress"
                dest.mkdir(exist_ok=True)
    elif adding:
        logging.info(f"Changing to the user ROMs directory: {output_dir.absolute()}")
        os.chdir(output_dir)

        logging.info("Creating to_compress folder...")
        to_compress_folder = output_dir / "to_compress"
        to_compress_folder.mkdir(exist_ok=True)
    
        logging.info("Creating unknown folder")
        unknown_folder = output_dir / "unknown"
        unknown_folder.mkdir(exist_ok=True)
    
        logging.info("Creating ambiguous folder")
        ambiguous_folder = output_dir / "ambiguous"
        ambiguous_folder.mkdir(exist_ok=True)

        logging.info("Creating ambiguous_to_compress folder")
        ambiguous_to_compress_folder = output_dir / "ambiguous_to_compress"
        ambiguous_to_compress_folder.mkdir(exist_ok=True)
    



            




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
            prefix = sony_match.group(1).lower() 
            if prefix in ['ulus', 'ules', 'ucus', 'uces', 'npjh', 'npuh'] and 'psp' in tied_consoles:
                return 'psp'
            if prefix in ['slus', 'sles', 'scus', 'sces', 'slpm'] and 'ps2' in tied_consoles:
                return 'ps2'
            if prefix in ['slps'] and 'psx' in tied_consoles: 
                return 'psx'

        nintendo_match = re.search(r'([A-Z0-9]{4}[EJPX][A-Z0-9])\s*Nintendo', header_text, re.IGNORECASE)
        if nintendo_match:
            code = nintendo_match.group(1)
            if code.startswith(('R', 'S', 'H')) and 'wii' in tied_consoles:
                return 'wii'
            if code.startswith('G') and 'gc' in tied_consoles:
                return 'gc'

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
    """
    Receives a path object of the game and returns to which console that game belongs to
    """
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
        

def get_destination(console,adding:bool,output_dir:Path,to_compress=False,):
    """Needs doc"""
    if console in ('unknown', None):
        return output_dir / 'unknown'

    if console == 'ambiguous':
        return output_dir / ('ambiguous_to_compress' if to_compress else 'ambiguous')

    if to_compress:
        return output_dir / 'to_compress' / f"{console}_to_compress"
    
    roms_base = output_dir if adding else output_dir / 'ROMs'
    return roms_base


def processor(file_types: dict, tempDir: tempfile,suffix_size_dict:dict,console_tag_serial:dict,output_dir:Path,adding:bool):
    """
    This function receives a dictionary for the type of file, a temporary Directory and a dictionary with the file sizes of each extension
    console combination
    
    It will move each file to the corresponding console directory, games that need to be extract will go to the "to_compress"
    before being moved to the final console directory

    The folder are created using the create_folders function

    This function will also delete the temporary directory used to store the extracted game files
    """    
    logging.info(f"Processor called — adding={adding}, output_dir={output_dir}")
    with tempDir as tempDir:

        for type, files in file_types.items():
            if type == 'to_compress' or type == 'not_to_compress':
                logging.debug("Moving files...")
                for file in files:
                    console= resolve_console(file,suffix_size_dict,console_tag_serial)
                    if type == 'to_compress':
                        dest = get_destination(console,adding,output_dir,to_compress=True)
                        dest.mkdir(parents=True,exist_ok=True)
                        if file.exists():
                            shutil.move(file,dest)
                            logging.debug(f"Moved {file.name} to {dest.name}")
                    elif type == 'not_to_compress':
                        dest = get_destination(console,adding,output_dir,to_compress=False)
                        dest.mkdir(parents=True,exist_ok=True)
                        if file.exists():
                            shutil.move(file,dest)
                            logging.debug(f"Moved {file.name} to {dest.name}")
            else:
                continue
                
    

                    




    


        
            

        


            
        
    

    

