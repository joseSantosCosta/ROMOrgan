from pathlib import Path
import re
file = Path() / 'test_files' / "Colin McRae Rally 2.0 [U] [SLUS-01222].rar"
file_name = file.name.lower()
clean_file_name = re.sub(r'[^a-zA-Z0-9-\s]', ' ', file_name)
file_name_tokens = clean_file_name.split()


print(file_name)
print(clean_file_name)
print(file_name_tokens)
print(file.suffix)
