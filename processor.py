from pathlib import Path
import shutil
import tempfile
import re

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

def normalize_file_name(file:Path) -> str:
    """
    This function receives a file, and returns its file name in lower case without any special characters besides the '-'
    """
    file_name = file.name.lower()
    clean_file_name = re.sub(r'[^a-zA-Z0-9-\s]', ' ', file_name)
    return clean_file_name


def size_name_serial_heuristic(file:Path,size_dict:dict,console_tag_serial:dict) -> str:

    #get candidates
    candidates = [candidate.lower() for candidate in extension_map[file.suffix]] if file.suffix in extension_map else []
    #generate console_score dict
    console_score = {key : 0 for key in candidates}

    #score by size
    suffix:str = file.suffix
    size_of_file:float = file.stat().st_size / (1024**2)#this is to get the size in megabytes
    for ext_console,sizes in size_dict.items():

        optimal_min = sizes[0] + 100
        optimal_max = sizes[1] - 100
        if ext_console[0] == suffix and (sizes[0] <= size_of_file and size_of_file <= sizes[1]) and ext_console[1] in console_score:
            console_score[ext_console[1].lower()] += 3
            if optimal_min <= size_of_file <= optimal_max and (sizes[1] - sizes[0] >= 300):
                console_score[ext_console[1].lower()] += 4
        elif ext_console[0] == suffix and (sizes[0] > size_of_file or size_of_file < sizes[1]):
            console_score[ext_console[1].lower()] -= 1


    normalized_file_name = normalize_file_name(file)
    file_name_tokens = normalized_file_name.split()
    extract_serial = re.search(r"([a-z]{4})[-._]?(\d{5})",normalized_file_name)
    extracted_serial = None
    if extract_serial:
            extracted_serial = f"{extract_serial.group(1)}-{extract_serial.group(2)}".lower()
    

    #score by name
    for match in candidates:
        tags = [t.lower() for t in console_tag_serial[match][0]]
        serials = [s.lower() for s in console_tag_serial[match][1]]
        tokens_in_tag = list(filter(lambda x : x in tags, file_name_tokens))
        console_score[match] += len(tokens_in_tag) 

        #score by serial
        if extracted_serial:
            serial_hits = list(filter(lambda p: extracted_serial.startswith(p), serials))
            if serial_hits:
                console_score[match] += 10
    
    if candidates == []:
        return 'unknown'
    
    max_val = max(console_score.values())

    if max_val == 0:
        return 'ambiguous'
    keys_max = [key for key, score in console_score.items() if score == max_val]
    return keys_max[0] if len(keys_max) == 1 else 'ambiguous'

            





def resolve_console(file:Path,suffix_size_dict,console_tag_serial:dict) -> str:
    """Needs doc"""
    suffix = file.suffix
    if suffix not in extension_map:
        print(f"{file.name} assigned unkown")
        return 'unknown'
    elif len(extension_map[suffix]) == 1:
        print(f"{file.name} assigned {extension_map[suffix][0]}")
        return extension_map[suffix][0]
    elif len(extension_map[suffix]) > 1:
        result = size_name_serial_heuristic(file,suffix_size_dict,console_tag_serial)
        return result
        


def get_destination(console, to_compress=False):
    """Needs doc"""
    if console in ('unknown', None):
        return Path() / 'unknown'

    if console == 'ambiguous':
        return Path() / ('ambiguous_to_compress' if to_compress else 'ambiguous')

    if to_compress:
        return Path() / 'to_compress' / f"to_compress_{console}"

    return Path() / 'ROMs' / console


def processor(file_types: dict, tempDir: tempfile,suffix_size_dict:dict):
    """
    This function receives a dictionary for the type of file, a temporary Directory and a dictionary with the file sizes of each extension
    console combination
    
    It will move each file to the corresponding console directory, games that need to be extract will go to the "to_compress"
    before being moved to the final console directory

    The folder are created using the create_folders function

    This function will also delete the temporary directory used to store the extracted game files
    """

    create_folders()
    
    for type, files in file_types.items():
        if type == 'to_compress' or type == 'not_to_compress':
            for file in files:
                console= resolve_console(file,suffix_size_dict)
                if type == 'to_compress':
                    dest = get_destination(console,to_compress=True)
                    dest.mkdir(parents=True,exist_ok=True)
                    if file.exists():
                        shutil.move(file,dest)
                        print(f"Moved {file.name} to {dest.name}")
                elif type == 'not_to_compress':
                    dest = get_destination(console,to_compress=False)
                    dest.mkdir(parents=True,exist_ok=True)
                    if file.exists():
                        shutil.move(file,dest)
                        print(f"Moved {file.name} to {dest.name}")
        else:
            continue
                
    

    tempDir.close()
    
                    




    


        
            

        


            
        
    

    

