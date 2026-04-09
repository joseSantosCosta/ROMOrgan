from pathlib import Path
import shutil
import tempfile
import csv

#This module will receive a dictionary from the classifier.classify_files() function 

console_dict = {
    "NES": ("NES", False),
    "SNES": ("SNES", False),
    "GB": ("GB", False),
    "GBA": ("GBA", False),
    "GENESIS": ("GENESIS", False),
    "N64": ("N64", False),
    "NDS": ("NDS", False),
    "3DS": ("3DS", False),
    "PS1": ("PS1", True),
    "PS2": ("PS2", True),
    "DC": ("DC", True),
    "Saturn": ("Saturn", True),
    "GC": ("GC", True),
    "WII": ("WII", True),
    "PSP": ("PSP", True)
}

extension_map = {
    #This dictionary has keys that represent possible ROM files extensions and their corresponding consoles
    ".nes": ["NES"],
    ".sfc": ["SNES"],
    ".smc": ["SNES"],
    ".gb": ["GB"],
    ".gbc": ["GB"],
    ".gba": ["GBA"],
    ".nds": ["NDS"],
    ".3ds": ["3DS"],
    ".cia": ["3DS"],
    ".gen": ["GENESIS"],
    ".md": ["GENESIS"],
    ".n64": ["N64"],
    ".z64": ["N64"],
    ".v64": ["N64"],
    ".iso": ["PS1", "PS2", "GC", "WII", "PSP"],
    ".bin": ["PS1", "Saturn", "GENESIS"],
    ".img": ["PS1", "PS2"],
    ".cue": ["PS1", "Saturn"],
    ".m3u": ["PS1", "Saturn"],
    ".gdi": ["DC"],
    ".cdi": ["DC"],
    ".chd": ["PSP"],
    ".wbfs": ["WII"],
    ".gcm": ["GC"],
    ".rvz": ["GC", "WII"],
    ".cso": ["PSP"],
    ".pbp": ["PS1", "PSP"],
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
    ROMs_folder = Path() / "ROMs"
    ROMs_folder.mkdir(exist_ok=True)

    to_compress_folder = Path() / "to_compress"
    to_compress_folder.mkdir(exist_ok=True)

    unknown_folder = Path() / "unknown"
    unknown_folder.mkdir(exist_ok=True)

    ambiguous_folder = Path() / "ambiguous"
    ambiguous_folder.mkdir(exist_ok=True)

    ambiguous_to_compress_folder = Path() / "ambiguous_to_compress"
    ambiguous_to_compress_folder.mkdir(exist_ok=True)

    for console,dir_flag in console_dict.items():
        dest = Path() / "ROMs" / f"{dir_flag[0]}"
        dest.mkdir(exist_ok=True)
        if dir_flag[1] == True:
            dest = Path() / "to_compress" / f"to_compress_{dir_flag[0]}"
            dest.mkdir(exist_ok=True)


def resolve_ambiguous_size(file:Path,suffix_size:dict) -> Path:
    return None



def resolve_console(file:Path) -> str:
    """Needs doc"""
    suffix = file.suffix
    if suffix not in extension_map:
        return 'unknown'
    elif len(extension_map[suffix]) == 1:
        return extension_map[suffix][0]
    elif len(extension_map[suffix]) > 1:
        return 'ambiguous'

def get_destination(console,to_compress = False):
    """Needs doc"""
    if console == 'unknown':
        return Path() / console
    
    if to_compress == False:
        if console == 'ambiguous':
            return Path() / console
        else:
            return Path() / 'ROMs' / console
    else:
        if console == 'ambiguous':
            return Path() / f"{console}_to_compress"
        else:
            return Path() / 'to_compress' / f"to_compress_{console}"


def processor(file_types: dict, tempDir: tempfile):
    """
    This function receives a dictionary and a temporary Directory 
    
    It will move each file to the corresponding console directory, games that need to be extract will go to the "to_compress"
    before being moved to the final console directory

    The folder are created using the create_folders function

    This function will also delete the temporary directory used to store the extracted game files
    """

    create_folders()
    
    for type, files in file_types.items():
        for file in files:
            console = resolve_console(file)
            if type == 'to_compress':
                dest = get_destination(console,to_compress=True)
                shutil.move(file,dest)
            elif type == 'not_to_compress':
                dest = get_destination(console,to_compress=False)
                shutil.move(file,dest)
            else:
                continue #In this part, I don't care about files that need to be extracted because there should be none
                
    

    tempDir.close()
    
                    




    


        
            

        


            
        
    

    

