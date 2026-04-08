import zipfile
from pathlib import Path
import tempfile

def get_zipped_files(to_extract_f:list,extracted_dir:dir,extracted:list) -> None:
    """
    This function receives a list of zip archives, a temp dir and a list of extracted files
    extracts the content of each zip file and deletes it after being extracted
 
    Returns a list of the extracted files
    
    The temporary directory must be kept alive until the processor finishes it job, it must not get deleted by the user
    """
    path_extracted_dir = Path(extracted_dir.name)
    for zip_f in to_extract_f:
        with zipfile.ZipFile(zip_f,'r') as to_extract_zips:
            to_extract_zips.extractall(path=path_extracted_dir)
        to_delete = Path(zip_f)
        to_delete.unlink(missing_ok=True) # deletes the zip folder that was just extracted
        to_extract_f.remove(zip_f) #removes it from the 'to_extract' list
    
    extracted.extend(path_extracted_dir.rglob('*'))