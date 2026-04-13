from pathlib import Path
import logging
import os

def clean_empty(output_dir:Path):
    logging.info("Cleaning empty folders")
    for dir in output_dir.glob('*'):
        if dir.is_dir() and len(os.listdir(dir)) == 0:
            logging.info(f"Deleted {dir.name} folder")
            dir.rmdir()
        elif dir.is_dir() and dir.name == 'to_compress':     
            for subdir in dir.glob('*'):
                if subdir.is_dir() and len(os.listdir(subdir)) == 0:
                    logging.info(f"Deleting {subdir.name}")
                    subdir.rmdir()
            logging.info(f"Deleting {dir.name}")
            if len(os.listdir(dir)) == 0:
                dir.rmdir()
                


                
