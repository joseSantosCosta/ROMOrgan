from pathlib import Path

def scan_directory(path:Path) -> list:
    """
    Scan the given directory recursively and returns a list of path objects of all files in that directory
    """
    input_directory = Path("test_files")
    all_files = []
    for file in input_directory.rglob('*'):
        if file.is_file():
            all_files.append(file)
    return all_files

    



    
    





