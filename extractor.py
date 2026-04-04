import zipfile
from pathlib import Path
import shutil
import logging


test_dir = Path("test_files")
workflow_file = Path("workflow.txt")

new_file = test_dir / "new_file.txt"

#print(test_dir.exists())
#print(workflow_file.exists())
#print(workflow_file.exists())
#print(new_file.exists())
#print(test_dir.absolute())

#p = Path("..").resolve() #in cases where we use shortcuts, if you want the real path use resolve, not absolute
#print(p)
#p = Path(__file__).resolve() #__file__ is the current file
#print(p)
#p = Path("~/dotfiles").expanduser() 
#print(p)
test_files = Path() / "test_files" #path.home returns the user directory
#print(p)


#create non compressed console folders
#look to the files that were downloaded
#check if there aren't any none relevant files
#zip files must be extracted and deleted after extraction
#each file goes to the corresponding console folder

console_tocompress_dict = {
    "GBA" : "tocompress_gba",
    "PSP" : "tocompress_psp",
    "PS1" : "tocompress_ps1",
    "PS2" : "tocompress_ps2",
    "WII" : "tocompress_wii",
    "SNES": "tocompress_SNES"
}

create_to_compress = Path("to_compress")
create_to_compress.mkdir(exist_ok=True)


for console,dir in console_tocompress_dict.items():
    to_compress = Path() / "to_compress" / console_tocompress_dict[console]
    to_compress.mkdir(exist_ok=True)





