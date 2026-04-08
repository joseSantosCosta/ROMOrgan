import csv
import tempfile
from pathlib import Path


def create_extracted_temp():
    extracted_dir = tempfile.TemporaryDirectory()
    extracted = []
    return extracted_dir,extracted

def create_file_types_dict() -> dict:
    file_types = {
        "to_compress":[],
        "not_to_compress":[],
        "to_extract":[]
    }
    return file_types

def create_valid_suffix_dict(file) -> dict:
    """
    This functions receives a tsv file and creates a dictionary based on it

    This dictionary has file extensions as keys and the values are tuples

    Each tuples stores the type of file that extension is associated with and a bool that lets us know if the file can be compressed

    Returns the dictionary
    """

    valid_suffix_file = csv.reader(file,delimiter='\t')
    valid_suffix_dict = {}

    for row in valid_suffix_file:
        valid_suffix_dict[row[0]] = (row[1],row[2])
    
    return valid_suffix_dict

def create_suffix_size_dict(file) -> dict:
    suffix_size_file = csv.reader(file,delimiter='\t')
    suffix_size_dict = {}

    for row in suffix_size_file:
        suffix_size_dict[(row[0],row[1])] = (row[2],row[3],row[4])
    return suffix_size_dict

#need to create a temporary file and its path