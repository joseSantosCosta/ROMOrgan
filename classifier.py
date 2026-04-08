from pathlib import Path
import csv

def classify_files(files: list,files_type:dict,valid_suffix:dict) -> None:
    """
    Receives the a list of path objects of the files that were in the input directory

    This function will add values to the files_type dict that is created outside of this function scope 
    """
    
    for file in files:
        suffix = file.suffix
        if suffix not in valid_suffix:
            continue
        else:

            f_type,compress = valid_suffix[suffix]
            if f_type == 'rom' or f_type == 'aux':
                if compress == 'Y':
                    files_type['to_compress'].append(file)
                else:
                    files_type['not_to_compress'].append(file)
            elif f_type == 'archive':
                files_type['to_extract'].append(file)
