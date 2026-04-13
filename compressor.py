import re
from pathlib import Path
import logging
import subprocess
import shutil


BASE_DIR = Path(__file__).parent.absolute()

CHDMAN_EXE = BASE_DIR / "tools" / "chdman.exe"
MAXCSO_EXE = BASE_DIR / "tools" / "maxcso.exe"
DOLPHIN_EXE = BASE_DIR / "tools" / "Dolphin-x64" / "DolphinTool.exe"

compression_tools_dict = {
    # --- CHDMAN (.chd) ---
    "PS1": {"tool": "chdman", "extension": ".chd"},
    "PS2": {"tool": "chdman", "extension": ".chd"},
    "SegaCD": {"tool": "chdman", "extension": ".chd"},
    "Saturn": {"tool": "chdman", "extension": ".chd"},
    "DC": {"tool": "chdman", "extension": ".chd"},
    "PCECD": {"tool": "chdman", "extension": ".chd"},
    "3DO": {"tool": "chdman", "extension": ".chd"},

    # --- DolphinTool (.rvz) ---
    "GC": {"tool": "dolphintool", "extension": ".rvz"},
    "WII": {"tool": "dolphintool", "extension": ".rvz"},

    # --- MaxCSO (.cso) ---
    "PSP": {"tool": "maxcso", "extension": ".cso"},
}

def identify_console(directory:Path):
    pattern = re.compile(r".+?(?=_)")
    match = re.match(pattern,directory.name).group(0)
    return match


def compressor(to_keep:bool):
    input_dir = Path() / 'to_compress'

    for dir in input_dir.glob('*'):
        console:str = identify_console(dir)

        if console not in compression_tools_dict:
            continue

        tool = compression_tools_dict[console]['tool']
        ext = compression_tools_dict[console]['extension']

        valid_inputs = ['.cue', '.iso', '.gdi', '.gcm', '.wbfs']

        for game in dir.rglob('*'):
            if not game.is_file() or game.suffix.lower() not in valid_inputs:
                continue

            output_file = game.with_suffix(ext)

            if compression_tools_dict[console]['tool'] == 'chdman':
                command = [str(CHDMAN_EXE),'createcd','-i',str(game),'-o',f"{str(output_file)}"]
                    
            elif compression_tools_dict[console]['tool'] == 'dolphintool':
                command = [str(DOLPHIN_EXE),'convert','-i',str(game),'-o',f"{str(output_file)}","-f","rvz"]

            elif compression_tools_dict[console]['tool'] == 'maxcso':
                command = [str(MAXCSO_EXE),'--out',str(output_file),str(game)]
            logging.info(f"Converting {game} to {ext}")
            result = subprocess.run(command,capture_output=True,text=True)

            if result.returncode == 0:
                logging.info(f"Sucess {output_file} created!")
                dest = Path() / 'ROMs' / console
                dest.mkdir(parents=True, exist_ok=True)
                logging.info(f"Moving {str(output_file)} to {dest.absolute()}")
                shutil.move(output_file,dest)

                import time
                time.sleep(1) 

                try:
                    original_ext = game.suffix.lower()
                    
                    if to_keep == False:
                       
                        if original_ext == '.cue':
                            with open(game, 'r', encoding='utf-8', errors='ignore') as f:
                                for track in re.findall(r'"([^"]+)"', f.read()):
                                    (game.parent / track).unlink(missing_ok=True)
                                    
                        if original_ext in ['.cue', '.gdi']:
                            for associated_file in game.parent.glob(f"{game.stem}*"):
                                if associated_file.suffix.lower() in ['.cue', '.bin', '.gdi', '.raw']:
                                    associated_file.unlink(missing_ok=True)

                        
                        game.unlink(missing_ok=True)
                        logging.info(f"Cleaned up original uncompressed files for {game.name}")
                        
                    else:
                        
                        new_dest = Path() / 'ROMs_Uncompressed' / console
                        new_dest.mkdir(parents=True, exist_ok=True) 
                        
                        
                        if original_ext in ['.cue', '.gdi']:
                            
                            if original_ext == '.cue':
                                with open(game, 'r', encoding='utf-8', errors='ignore') as f:
                                    for track in re.findall(r'"([^"]+)"', f.read()):
                                        track_path = game.parent / track
                                        if track_path.exists():
                                            shutil.move(str(track_path), str(new_dest))
                            
                            
                            for associated_file in game.parent.glob(f"{game.stem}*"):
                                if associated_file.suffix.lower() in ['.cue', '.bin', '.gdi', '.raw']:
                                    if associated_file.exists(): 
                                        shutil.move(str(associated_file), str(new_dest))
                        
        
                        if game.exists():
                            shutil.move(str(game), str(new_dest))
                            
                        logging.info(f"Moved original uncompressed files for {game.name} to {new_dest.absolute()}")

                except Exception as e:
                    logging.error(f"⚠️ Error handling original files for {game.name}: {e}")
    




            










