import sys
from pathlib import Path
import logging
#home made modules
import rules
import scanner
import classifier
import extractor
import processor
import compressor

logging.basicConfig(
    level=logging.INFO, # Change to logging.INFO later if DEBUG is too noisy
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

files_type_dict = rules.create_file_types_dict()

valid_suffix_dict = rules.create_valid_suffix_dict('valid_suffix.txt')

suffix_size_dict = rules.create_suffix_size_dict('suffix_sizes.txt')

console_tag_serial_dict = rules.create_tag_serial_dict('console_tags_serials.txt')

tempDir,extracted_list = rules.create_extracted_temp()


dir_to_scan = Path('test_files')
files = scanner.scan_directory(dir_to_scan)



classifier.classify_files(files,files_type_dict,valid_suffix_dict)


while files_type_dict['to_extract']:
    copy_to_extract_files = files_type_dict['to_extract'].copy()
    files_type_dict['to_extract'].clear()
    extracted_list.clear() #this is the list of files that were already extracted, it makes sense to clear it before in order to make sure we are not always dealing with the same files
    extractor.get_archive_files(copy_to_extract_files,tempDir,extracted_list)
    classifier.classify_files(extracted_list,files_type_dict,valid_suffix_dict)


#processor(classified)
processor.create_folders() 
processor.processor(files_type_dict,tempDir,suffix_size_dict,console_tag_serial_dict)

#compress the files
compressor.compressor() #this will look directly into the 'to_compress' directory created




    





