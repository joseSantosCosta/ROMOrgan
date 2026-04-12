from pathlib import Path
import csv
import logging



def classify_files(files: list,files_type:dict,valid_suffix:dict) -> None:
    """
    Receives the a list of path objects of the files that were in the input directory

    This function will add values to the files_type dict that is created outside of this function scope 
    """
    for file in files:
        logging.debug(f"Classifying {file.name}")
        suffix = file.suffix
        if suffix not in valid_suffix:
            logging.debug(f"{file.name} doesn't have a valid suffix")
            continue
        else:
            f_type,compress = valid_suffix[suffix]
            if f_type == 'rom' or f_type == 'aux':
                if compress == 'Y':
                    logging.debug(f"{file.name} was classified as a to_compress file")
                    files_type['to_compress'].append(file)
                else:
                    logging.debug(f"{file.name} was classified as not needing compression")
                    files_type['not_to_compress'].append(file)
            elif f_type == 'archive':
                logging.debug(f"{file.name} is an archive that needs to be extracted")
                files_type['to_extract'].append(file)
