import zipfile
from pathlib import Path
import logging
import patoolib
from patoolib.util import PatoolError

def get_archive_files(to_extract_f:list,extracted_dir:dir,extracted:list,to_keep:bool) -> None:
    """
    This function receives a list of zip archives, a temp dir and a list of extracted files,
    extracts the content of each zip file and deletes it after being extracted
 
    Returns a list of the extracted files
    
    The temporary directory must be kept alive until the processor finishes it job, it must not get deleted by the user
    """
    path_extracted_dir = Path(extracted_dir.name)
    for archive in to_extract_f:
        logging.info(f"Extracting {archive.name}")
        try:
            patoolib.extract_archive(str(archive.absolute()),verbosity=-2,interactive = False,outdir=str(path_extracted_dir.absolute()))
            logging.info(f"Extracted {archive.name}")
            if to_keep == False:
                logging.info(f"Deleting {archive.name}")
                archive.unlink(missing_ok=True)
        except PatoolError as e:
            logging.error(f"Failed to extract {archive.name}: {e}")
            print(f"Error extracting {archive.name}. Skipping deletion.")
    
    new_files = [file for file in path_extracted_dir.rglob('*') if file.is_file()]
    for file in new_files:
        if file not in extracted:
            extracted.append(file)

