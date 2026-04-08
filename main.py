import zipfile
from pathlib import Path
import shutil
import logging
import csv
import tempfile
#home made mdoules
import rules
import scanner
import classifier
import extractor
import processor

#rules = rules()

files_type_dict = rules.create_file_types_dict()

valid_suffix_dict = rules.create_valid_suffix_dict('valid_suffix.txt')

tempDir,extracted_list = rules.create_extracted_temp()

#files = scan()
#the directory to scan will be decided by user input -> will take care of that later, for now I'll work with the test directory

dir_to_scan = Path('test_files')
files = scanner.scan_directory(dir_to_scan)

#classified = classify(files)

classifier.classify_files(files,files_type_dict,valid_suffix_dict)

#while houver ficheiros para extrair:
    #extracted = extract(...)
    #classified = classify(extracted)

while files_type_dict['to_extract']:
    copy_to_extract_files = files_type_dict['to_extract'].copy()
    files_type_dict['to_extract'].clear()
    extracted_list.clear() #this is the list of files that were already extracted, it makes sense to clear it before in order to make sure we are not always dealing with the same files
    extractor.get_zipped_files(copy_to_extract_files,tempDir,extracted_list)
    classifier.classify_files(extracted_list,files_type_dict,valid_suffix_dict)


#processor(classified)
processor.create_folders() 
processor.processor(files_type_dict,tempDir)


    
    





