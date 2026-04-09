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
    valid_suffix_dict = {}
    with open(file,'r') as f:
        valid_suffix_file = csv.reader(f,delimiter='\t')
        for row in valid_suffix_file:
            valid_suffix_dict[row[0]] = (row[1],row[2])
    
    return valid_suffix_dict

def create_suffix_size_dict(file) -> dict:
    suffix_size_dict = {}
    with open(file,'r') as f:
        suffix_size_file = csv.reader(f,delimiter='\t')
        for row in suffix_size_file:
            suffix_size_dict[(row[0],row[1])] = (int(row[2]), int(row[3]),row[4])
    return suffix_size_dict

def create_console_tags_serials_dict(file) -> dict:
    console_tag_serials_dict = {}
    with open(file,'r') as f:
        console_tag_serials_file = csv.reader(f,delimiter='\t')
        for row in console_tag_serials_file:
            console_tag_serials_dict[row[0]] = (row[1].split(','),row[2].split(','))
    return console_tag_serials_dict

print(create_console_tags_serials_dict('console_tags_serials.txt'))