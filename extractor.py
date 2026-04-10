import zipfile
from pathlib import Path
import logging

logging.basicConfig(filename='extractor.log',level=logging.DEBUG)

def get_zipped_files(to_extract_f:list,extracted_dir:dir,extracted:list) -> None:
    """
    This function receives a list of zip archives, a temp dir and a list of extracted files,
    extracts the content of each zip file and deletes it after being extracted
 
    Returns a list of the extracted files
    
    The temporary directory must be kept alive until the processor finishes it job, it must not get deleted by the user
    """
    path_extracted_dir = Path(extracted_dir.name)
    for zip_f in to_extract_f:
        logging.debug(f"Extracting {zip_f.name}")
        with zipfile.ZipFile(zip_f,'r') as to_extract_zips:
            for file in to_extract_zips.infolist():
                target_path = path_extracted_dir / file.filename
                if target_path.exists():
                    print(f"Skipping {file.filename}: File already exists")
                else:
                    to_extract_zips.extract(file,path_extracted_dir)
                    print(f"Extracted: {file.filename}")
        logging.debug(f"Deleting {zip_f.name}, the content of it was already extracted ")
        to_delete = Path(zip_f)
        to_delete.unlink(missing_ok=True) # deletes the zip folder that was just extracted
    
    extracted.extend([file for file in path_extracted_dir.rglob('*') if file.is_file()])