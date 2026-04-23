import requests
from pathlib import Path
import logging
import os
import shutil
import subprocess

TOOLS_DIR = Path() / 'tools/'
ALL_TOOLS = ['Dolphin-x64','chdman.exe','maxcso.exe','UnRAR.exe']


def check_tools():
    """
    This function checks the tools folder and return a list of missing tools, if no tool is missing, it returns None
    """
    if shutil.which('7z') or shutil.which("7za"):
        logging.info("7zip is installed in this computer. Continuing the process...")
    else:
        raise ValueError("You don't have 7zip installed in your computer, please install it!")
    missing_tools = []
    logging.info("Checking if you have all the necessary tools")
    tools_in_dir = [tool.name for tool in TOOLS_DIR.glob('*')]
    for tool in ALL_TOOLS:
        if tool not in tools_in_dir:
            logging.info(f"The following tool {tool} is missing.")
            missing_tools.append(tool)
    return missing_tools if missing_tools else None

def download_and_extract_tool(url: str, archive_name: str, file_to_isolate: str = None) -> None:
    """
    Downloads an archive, extracts it using 7z, optionally isolates a specific file, 
    and cleans up the downloaded archive.
    """
    logging.info(f"Downloading from {url}...")
    with requests.get(url, timeout=10) as r:
        if r.status_code == requests.codes.ok:
            with open(archive_name, 'wb') as f:
                f.write(r.content)
            logging.info(f"Successfully downloaded {archive_name}")

            extract_dir = f"{archive_name}_temp" if file_to_isolate else "."
            if extract_dir != ".":
                os.makedirs(extract_dir, exist_ok=True)

            logging.info(f"Extracting {archive_name}...")
            subprocess.run([
                "7z", "x", archive_name, f"-o{extract_dir}", "-y"
            ], check=True)

            if file_to_isolate:
                target_path = Path(extract_dir) / file_to_isolate
                shutil.move(target_path, Path())
                logging.info(f"Moved {file_to_isolate} to working directory.")
                shutil.rmtree(Path(extract_dir))  # Delete the temp folder

            Path(archive_name).unlink(missing_ok=True)
            logging.info(f"Cleaned up {archive_name}")
            
        else:
            logging.error(f"Failed to download {archive_name}. Status code: {r.status_code}")

def get_missing_tools(missing_tools: list) -> None:
    """
    This function receives a list of missing tools, downloads them and extracts them
    """
    logging.info(f"Changing working directory to {TOOLS_DIR.absolute()}")
    os.chdir(TOOLS_DIR)

    if not missing_tools or missing_tools == [None]:
        logging.info("You have all the necessary tools, starting the process...")
        return
    tool_configs = {
        'chdman.exe': {
            'url': "https://github.com/mamedev/mame/releases/download/mame0287/mame0287b_arm64.exe",
            'archive_name': 'mame.exe',
            'file_to_isolate': 'chdman.exe'
        },
        'Dolphin-x64': {
            'url': "https://dl.dolphin-emu.org/releases/2603a/dolphin-2603a-x64.7z",
            'archive_name': 'Dolphin.7z',
            'file_to_isolate': None
        },
        'maxcso.exe': {
            'url': "https://github.com/unknownbrackets/maxcso/releases/download/v1.13.0/maxcso_v1.13.0_windows.7z",
            'archive_name': 'maxcso.7z',
            'file_to_isolate': None
        },
        'UnRAR.exe': {
            'url': "https://www.rarlab.com/rar/unrarw64.exe",
            'archive_name': 'unrar_installer.exe',
            'file_to_isolate': 'unrar.exe'
        }
    }

    for tool in missing_tools:
        if tool in tool_configs:
            logging.info(f"--- Processing {tool} ---")
            config = tool_configs[tool]
            
            download_and_extract_tool(
                url=config['url'],
                archive_name=config['archive_name'],
                file_to_isolate=config['file_to_isolate']
            )
        elif tool is not None:
            logging.warning(f"Tool '{tool}' is not recognized in the configuration dictionary.")




                    
                



            





                

            



