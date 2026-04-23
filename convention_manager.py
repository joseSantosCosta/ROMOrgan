from pathlib import Path
import logging

#possible_conventions = ['ES-DE','RetroArch','Full name','Manufacture/System']
#possible_subs = ['','alphabetical','region']

console_dict = {
    # --- Nintendo ---
    "NES": ("nes", False),
    "SNES": ("snes", False),
    "N64": ("n64", False),
    "GB": ("gb", False),
    "GBC": ("gbc", False),
    "GBA": ("gba", False),
    "NDS": ("nds", False),
    "3DS": ("3ds", False),
    "VB": ("virtualboy", False),
    "POKEMINI": ("pokemini", False),
    "SWITCH": ("switch", False),
    "GC": ("gc", True),
    "WII": ("wii", True),
    "WIIU": ("wiiu", True),

    # --- Sony ---
    "PS1": ("psx", True),
    "PS2": ("ps2", True),
    "PS3": ("ps3", True),
    "PS4": ("ps4", False),
    "PSP": ("psp", True),
    "VITA": ("psvita", False),

    # --- Sega ---
    "SG1000": ("sg1000", False),
    "SMS": ("mastersystem", False),
    "GENESIS": ("megadrive", False),
    "32X": ("sega32x", False),
    "SegaCD": ("segacd", True),
    "Saturn": ("saturn", True),
    "DC": ("dreamcast", True),
    "GG": ("gamegear", False),

    # --- Microsoft ---
    "XBOX": ("xbox", True),
    "X360": ("xbox360", True),

    # --- Atari ---
    "A2600": ("atari2600", False),
    "A5200": ("atari5200", False),
    "A7800": ("atari7800", False),
    "LYNX": ("atarilynx", False),
    "JAG": ("atarijaguar", False),

    # --- NEC / TurboGrafx ---
    "PCE": ("tg16", False),
    "PCECD": ("tg-cd", True),

    # --- SNK / Neo Geo ---
    "NEOGEO": ("neogeo", False),
    "NGP": ("ngp", False),

    # --- Microcomputers & Others ---
    "3DO": ("3do", True),
    "WS": ("wonderswan", False),
    "INTV": ("intellivision", False),
    "COLECO": ("colecovision", False),
    "VEC": ("vectrex", False),
    "AMIGA": ("amiga", False),
    "C64": ("c64", False),
    "ZXS": ("zxspectrum", False),
    "MSX": ("msx", False),
    "CPC": ("amstradcpc", False),
    "AppleII": ("apple2", False),
}

def create_folder_ESDE(output_dir:Path)->None:
    """
    This function will create the library folders in the output dir selected by the user based on the ES-DE convention

    This function assumes that the user is creating the library from scratch (at least for now)
    """
    for console,dir_flag in console_dict.items():
            logging.info(f"Creating ROMs/{console} subfolder")
            dest = output_dir / "ROMs" / f"{console}"
            dest.mkdir(exist_ok=True)
            if dir_flag[1] == True:
                logging.info(f"Creating to_compress/{console} folder")
                dest = output_dir / "to_compress" / f"{console}_to_compress"
                dest.mkdir(exist_ok=True)




