from pathlib import Path
import logging
import os

def clean_empty(output_dir: Path, adding: bool, existing_folders: set):
    logging.info("Cleaning empty folders")
    for dir in output_dir.glob('*'):
        if not dir.is_dir():
            continue
        if dir.name in existing_folders:
            continue
        if len(os.listdir(dir)) == 0:
            logging.info(f"Deleted {dir.name} folder")
            dir.rmdir()
        elif dir.name == 'to_compress':
            for subdir in dir.glob('*'):
                if subdir.is_dir() and len(os.listdir(subdir)) == 0:
                    logging.info(f"Deleting {subdir.name}")
                    subdir.rmdir()
            if len(os.listdir(dir)) == 0:
                logging.info(f"Deleting {dir.name}")
                dir.rmdir()
                


                
