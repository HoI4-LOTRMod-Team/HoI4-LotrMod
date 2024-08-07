import os
import re
import math

# Define the directories to search
directories = ['common', 'history']

# Define the tokens and operators
tokens = [
    'weekly_manpower',
    'manpower_per_military_factory',
    'garrison_manpower_need',
    'exiled_government_weekly_manpower',
    'has_manpower',
    'add_manpower',
    'manpower'
]

operators = ['<', '>', '=']

# Create a regex pattern to match the required format
pattern = re.compile(r'[\s{\n](' + '|'.join(tokens) + r')\s*(' + '|'.join(map(re.escape, operators)) + r')\s*(\d+)')

def process_file(file_path):
    print(f'Processing file: {file_path}...')
    with open(file_path, 'r') as file:
        content = file.read()

    def replace_match(match):
        token = match.group(1)
        operator = match.group(2)
        number = int(match.group(3))
        new_number = number // 10
        return f'{match.group(0)[:match.start(3) - match.start(0)]}{new_number}'

    new_content = re.sub(pattern, replace_match, content)

    with open(file_path, 'w') as file:
        file.write(new_content)

def main():
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.txt'):
                    process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()