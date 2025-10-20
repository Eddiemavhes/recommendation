def clean_file(filepath):
    # Read the file in binary mode
    with open(filepath, 'rb') as file:
        content = file.read()
    
    # Remove null bytes
    cleaned = content.replace(b'\x00', b'')
    
    # Write back in text mode with UTF-8 encoding
    with open(filepath, 'w', encoding='utf-8', newline='\n') as file:
        file.write(cleaned.decode('utf-8', errors='ignore'))
    
    print(f"Cleaned {filepath}")

# Clean both files
files_to_clean = [
    r'jobs\signals.py',
    r'jobs\services\adzuna_service.py'
]

for file in files_to_clean:
    clean_file(file)