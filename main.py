import sys
import os
import threading
import logging
from pathlib import Path
import FreeSimpleGUI as sg

import rules
import scanner
import classifier
import extractor
import processor
import compressor
import cleaner
import GUI_creator

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("main.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)


class GUIHandler(logging.Handler):
    def __init__(self, window,key):
        super().__init__()
        self.window = window
        self.key = key

    def emit(self,record):
        msg = self.format(record)
        self.window.write_event_value(self.key,msg)








def back_end(input_dir:Path,output_dir:Path,keep_extract:bool,keep_compress:bool,from_scratch:bool,adding:bool):
    existing_folders = {f.name for f in output_dir.iterdir() if f.is_dir()}
    BASE_DIR = Path(__file__).parent.absolute()
    logging.info("BOOTING ROM ORGANIZER...")
    logging.info("Loading rules...")
    files_type_dict = rules.create_file_types_dict()
    valid_suffix_dict = rules.create_valid_suffix_dict(BASE_DIR / 'valid_suffix.txt')
    suffix_size_dict = rules.create_suffix_size_dict(BASE_DIR / 'suffix_sizes.txt')
    console_tag_serial_dict = rules.create_tag_serial_dict(BASE_DIR / 'console_tags_serials.txt')
    tempDir, extracted_list = rules.create_extracted_temp()

    logging.info("Scanning directory...")
    files = scanner.scan_directory(Path(input_dir))

    classifier.classify_files(files, files_type_dict, valid_suffix_dict)

    while files_type_dict['to_extract']:
        copy_list = files_type_dict['to_extract'].copy()
        files_type_dict['to_extract'].clear()
        extracted_list.clear()
        extractor.get_archive_files(copy_list, tempDir, extracted_list,keep_extract)
        classifier.classify_files(extracted_list, files_type_dict, valid_suffix_dict)

    os.chdir(output_dir)
    logging.info("Output directory set.")

    processor.create_folders(from_scratch,adding,output_dir)
        
    processor.processor(files_type_dict, tempDir, suffix_size_dict, console_tag_serial_dict,output_dir,adding)

    compressor.compressor(keep_compress,adding)
    cleaner.clean_empty(output_dir,adding,existing_folders)

    logging.info(">>> COMPLETE <<<")

input_dir:Path = None
output_dir:Path = None

#Creating the UI
window = GUI_creator.create_first_window()



#setting the logger
gui_handler = GUIHandler(window,"-CONSOLE OUTPUT-")
gui_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logging.getLogger().addHandler(gui_handler)
from_scratch = False
adding = False


thread = None
while True:
    events, values = window.read(timeout=100)

    if events == sg.WIN_CLOSED:
        break

    elif events == '-FROM SCRATCH-':
        from_scratch = True
        window.close()
        window = GUI_creator.create_add_window()
        gui_handler.window = window
        

    elif events == '-ADD GAMES-':
        adding = True
        window.close()
        window = GUI_creator.create_add_window(adding=True)
        gui_handler.window = window


    elif events == '-ABORT BUTTON-':
        if thread and thread.is_alive():
            pass  
        else:
            break 

    elif events == '-START_BUTTON-':
        keep_extract = values['-KEEP_EXTRACT-']
        keep_compress = values['-KEEP_COMPRESS-']
        input_dir = Path(values['-INPUT_FOLDER-'])
        output_dir = Path(values['-OUTPUT_FOLDER-'])
        thread = threading.Thread(
            target=back_end,
            args=(input_dir, output_dir, keep_extract, keep_compress, from_scratch, adding),
            daemon=True
        )
        thread.start()

    elif events == "-CONSOLE OUTPUT-":
        window["-CONSOLE OUTPUT-"].print(values['-CONSOLE OUTPUT-'])

    
    if thread and not thread.is_alive():
        window['-ABORT BUTTON-'].update("EXIT")
        thread = None

            # force full exit








