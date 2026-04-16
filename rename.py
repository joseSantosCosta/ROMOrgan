from pathlib import Path
import scanner
import os
from twoWayDict import twoWayDict
import processor
import rules
from collections import Counter
import logging

suffix_size_dict = rules.create_suffix_size_dict('suffix_sizes.txt')
console_tag_serial = rules.create_tag_serial_dict('console_tags_serials.txt')

CONSOLE_ALIASES = {
    # --- Nintendo ---
    "NES": ["NES", "Nintendo Entertainment System", "Famicom", "Nintendo"],
    "SNES": ["SNES", "Super Nintendo", "Super Famicom", "Super Nintendo Entertainment System", "SFC"],
    "N64": ["N64", "Nintendo 64"],
    "GB": ["GB", "Game Boy", "Gameboy", "Nintendo Game Boy"],
    "GBC": ["GBC", "Game Boy Color", "Gameboy Color"],
    "GBA": ["GBA", "Game Boy Advance", "Gameboy Advance"],
    "NDS": ["NDS", "DS", "Nintendo DS"],
    "3DS": ["3DS", "Nintendo 3DS"],
    "VB": ["VB", "Virtual Boy", "Nintendo Virtual Boy"],
    "POKEMINI": ["Pokemon Mini", "PokeMini"],
    "SWITCH": ["SWITCH", "Nintendo Switch", "NS"],
    "GC": ["GC", "GameCube", "Game Cube", "Nintendo GameCube", "GCN"],
    "WII": ["WII", "Wii", "Nintendo Wii"],
    "WIIU": ["WIIU", "Wii U", "Nintendo Wii U"],

    # --- Sony ---
    "PS1": ["PS1", "PSX", "PlayStation", "PlayStation 1", "Sony PlayStation"],
    "PS2": ["PS2", "PlayStation 2", "Sony PlayStation 2"],
    "PS3": ["PS3", "PlayStation 3", "Sony PlayStation 3"],
    "PS4": ["PS4", "PlayStation 4", "Sony PlayStation 4"],
    "PSP": ["PSP", "PlayStation Portable", "Sony PSP"],
    "VITA": ["VITA", "PS Vita", "PlayStation Vita", "PSVita"],

    # --- Sega ---
    "SG1000": ["SG1000", "SG-1000", "Sega SG-1000"],
    "SMS": ["SMS", "Master System", "Sega Master System"],
    "GENESIS": ["GENESIS", "Mega Drive", "Sega Genesis", "Sega Mega Drive", "Megadrive"],
    "32X": ["32X", "Sega 32X", "Sega Genesis 32X"],
    "SegaCD": ["SegaCD", "Sega CD", "Mega CD", "Sega Mega-CD"],
    "Saturn": ["Saturn", "Sega Saturn"],
    "DC": ["DC", "Dreamcast", "Sega Dreamcast"],
    "GG": ["GG", "Game Gear", "Sega Game Gear"],

    # --- Microsoft ---
    "XBOX": ["XBOX", "Xbox", "Microsoft Xbox", "Original Xbox"],
    "X360": ["X360", "Xbox 360", "Microsoft Xbox 360"],

    # --- Atari ---
    "A2600": ["A2600", "Atari 2600", "VCS"],
    "A5200": ["A5200", "Atari 5200"],
    "A7800": ["A7800", "Atari 7800"],
    "LYNX": ["LYNX", "Atari Lynx", "Lynx"],
    "JAG": ["JAG", "Atari Jaguar", "Jaguar"],

    # --- NEC / TurboGrafx ---
    "PCE": ["PCE", "PC Engine", "TurboGrafx-16", "TG16", "TurboGrafx"],
    "PCECD": ["PCECD", "PC Engine CD", "TurboGrafx-CD", "TGCD", "TurboGrafx CD"],

    # --- SNK / Neo Geo ---
    "NEOGEO": ["NEOGEO", "Neo Geo", "Neo-Geo MVS", "Neo-Geo AES", "NeoGeo AES"],
    "NGP": ["NGP", "Neo Geo Pocket", "NGPC", "Neo Geo Pocket Color"],

    # --- Microcomputers & Others ---
    "3DO": ["3DO", "Panasonic 3DO", "3DO Interactive Multiplayer"],
    "WS": ["WS", "WonderSwan", "Bandai WonderSwan", "WSC", "WonderSwan Color"],
    "INTV": ["INTV", "Intellivision", "Mattel Intellivision"],
    "COLECO": ["COLECO", "ColecoVision", "Coleco"],
    "VEC": ["VEC", "Vectrex"],
    "AMIGA": ["AMIGA", "Commodore Amiga", "Amiga 500"],
    "C64": ["C64", "Commodore 64", "C-64"],
    "ZXS": ["ZXS", "ZX Spectrum", "Sinclair ZX Spectrum"],
    "MSX": ["MSX", "Microsoft MSX"],
    "CPC": ["CPC", "Amstrad CPC"],
    "AppleII": ["AppleII", "Apple II", "Apple 2"],
}

input_directory = Path('test_input')
console_aliases = twoWayDict(CONSOLE_ALIASES)

def check_directory(directory:Path) -> tuple:
    """
    Receives a directory path object and scans all the files that are inside of it

    Returns a tuple where the first entry is the name of the directory in lower case and the second entry is the list of all files 
    """
    directory_name = directory.name
    all_files = scanner.scan_directory(directory) if len(os.listdir(directory)) > 0 else None 
    return directory_name, all_files, 

def change_dir_name(roms_dir:Path):
    """
    Receives a Path (meant to be the ROM path of the user) and changes the name of each directory bases on the console dict alias

    It does this so it works correctly with the rest of the names in the script

    Return a dict where each key corresponds to the new name of a directory and the value corresponds  to the old name
    """
    all_folder_names:list = [dir.name for dir in roms_dir.glob('*') if dir.is_dir()]
    all_aliases = [alias.lower() for group in CONSOLE_ALIASES.values() for alias in group]
    old_dir_name = ""
    new_dir_name = ""
    new_to_old_dict = {}
    for dir_name in all_folder_names:
        if dir_name not in CONSOLE_ALIASES:
            logging.info("A folder name didnt match the convention")
            if dir_name.lower() in all_aliases: 
                old_dir_name = dir_name
                logging.info(f"The old dir name is {old_dir_name}")
                new_dir_name = console_aliases.inverseDict()[dir_name.lower()]
                logging.info(f"The new dir name is {new_dir_name}")
                logging.info(f"Changing the name of {old_dir_name} to {new_dir_name}")
                os.rename(Path(roms_dir / old_dir_name),Path(roms_dir / new_dir_name))
                new_to_old_dict[new_dir_name] = old_dir_name
            else:
                dir_path = Path(roms_dir/dir_name)
                if len(os.listdir(dir_path)) > 0:
                    logging.info(f"Couldn't fild to which console the name {dir_name} matches to: checking the games in it to find a match...")
                    list_of_consoles = []
                    for game in dir_path.glob('*'):
                        console_of_game = processor.resolve_console(game,suffix_size_dict,console_tag_serial)
                        logging.info(f"There's a {console_of_game} game in {dir_path.name}")
                        list_of_consoles.append(console_of_game)
                    consoles_mentioned = Counter(list_of_consoles)
                    new_dir_name = max(consoles_mentioned,key=consoles_mentioned.get)
                    logging.info(f"Found a match! The name {dir_path.name} is actually {new_dir_name}. Renaming...")
                    os.rename(dir_path,Path(roms_dir/new_dir_name))  
                    new_to_old_dict[new_dir_name] = dir_path.name  
                else:
                    logging.info(f"Can't find the possible console to {dir_name}, leaving it as it is")
                    
    return new_to_old_dict if new_to_old_dict else None

def original_dir_name(roms_dir:Path,new_to_old:dict):
    for dir in roms_dir.glob('*'):
        if dir.name in new_to_old:
            logging.info(f"Renaming {dir.name} back to {new_to_old[dir.name]}...")
            os.rename(Path(roms_dir / dir.name),Path(roms_dir/new_to_old[dir.name]))





                


            



