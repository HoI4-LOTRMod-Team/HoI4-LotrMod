import os
import re

def process_string(s):
    # Convert to lowercase and replace spaces with underscores
    processed = re.sub(r'\W+', '', s.lower().replace(' ', '_'))
    return processed

def find_and_process_strings(directory):
    # Regex to find strings enclosed in quotation marks
    pattern = r'"(.*?)"'

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find all matches and process them
                matches = re.findall(pattern, content)
                for match in matches:
                    processed = process_string(match)
                    print(f'{processed}:0 "{match}"')
                    # Replace the original string in quotation marks with the processed variant
                    content = content.replace(f'"{match}"', processed)

                # Write the modified content back to the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

# Replace 'your_directory_path' with the path to the directory you want to process
directory_path = r'C:\Users\kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\military_industrial_organization'
find_and_process_strings(directory_path)