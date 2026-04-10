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
            suffix_size_dict[(row[0],row[1])] = (float(row[2]), float(row[3]),row[4])
    return suffix_size_dict

def create_tag_serial_dict(file) -> dict:
    tag_serial_dict = {}
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            console_key = row[0]
            tags = row[1].split(',')
            serials = row[2].split(',') if len(row) > 2 and row[2].strip() else []
            tag_serial_dict[console_key] = (tags, serials)
    return tag_serial_dict

