from pathlib import Path
import logging


def scan_directory(path:Path) -> list:
    """
    Scan the given directory recursively and returns a list of path objects of all files in that directory
    """
    all_files = []
    logging.debug("Going through files...")
    for file in path.rglob('*'):
        logging.debug(f"Scanning {file.name}")
        if file.is_file():
            all_files.append(file)
    logging.debug(f"The list of files is: {all_files}")
    return all_files




    
    





