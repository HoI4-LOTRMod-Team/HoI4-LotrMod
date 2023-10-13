import re


# This script lets you find the differences in two loc files


def custom_yaml_parser(file_content):
    data = {}
    duplicate_keys = set()
    current_key = None

    lines = file_content.split('\n')
    for line in lines:
        # Use regular expression to extract key, value, and string
        match = re.match(r'^\s*([a-zA-Z0-9_]+)(:\d+)?\s+"(.+)"\s*$', line)
        if match:
            key, _, value = match.groups()
            if key in data:
                duplicate_keys.add(key)
            data[key] = value
        elif current_key:
            # Handle multi-line strings
            data[current_key] += f'\n{line.strip()}'

    if duplicate_keys:
        print("Warning: Duplicate keys found in the YAML file:", ', '.join(duplicate_keys))

    return data

def load_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            return custom_yaml_parser(file_content)
    except Exception as e:
        print(f"Error loading YAML file {file_path}: {e}")
        return {}

vanilla = load_yaml(r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV BETA\localisation\english\tank_modules_l_english.yml')
custom = load_yaml(r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\localisation\english\tank_modules_l_english.yml')

#for key, value in data.items():
#    print(f"Key: {key}")
#    print(f"Value: {value}")
#    print("-" * 20)

for key, value in custom.items():
    if key not in vanilla:
        print(key+":0 \""+value+"\"")
    else:
        if value != vanilla[key]:
            print(key+":0 \""+value+"\"")