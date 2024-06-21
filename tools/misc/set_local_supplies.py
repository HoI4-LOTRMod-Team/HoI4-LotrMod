import os
import re
import random
import math  # Import the math module

def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))

def calculate_new_value(manpower, state_category, provinces, line_count):

    base_value = (manpower / 25000) / (len(provinces)*1.35)
    
    # flat modifier
    category_values = {
        'wasteland': -999,
        'enclave': -20,
        'tiny_island': -999,
        'pastoral': -10,
        'small_island': -999,
        'rural': -8,
        'town': -5,
        'large_town': -3,
        'city': 0,
        'large_city': 1,
        'metropolis': 2,
        'megalopolis': 3,
        'darkground': 5,
    }
    base_value += category_values.get(state_category, 0)  # Default to 0 if category not found
    
    # Multiply by factors
    line_factor = lerp(0.6, 1.35, (line_count - 20) / (40 - 20))
    random_factor = random.uniform(0.7, 1.3)
    
    final_value = base_value * line_factor * random_factor
    
    final_value = math.floor(final_value)
    final_value = float(max(0, min(final_value, 16)))
    
    return final_value

def parse_and_update_file(file_path):
    with open(file_path, 'r+') as file:
        content = file.read()

        # Extracting values
        manpower = int(re.search(r'manpower\s*=\s*(\d+)', content).group(1))
        state_category = re.search(r'state_category\s*=\s*(.*?)', content).group(1)
        provinces = list(map(int, re.search(r'provinces\s*=\s*\{\s*([\d\s]+)\s*\}', content).group(1).split()))

        # Call the function with extracted values
        new_value = calculate_new_value(manpower, state_category, provinces, len(file.readlines()))

        # Replace the local_supplies value
        new_content = re.sub(r'local_supplies\s*=\s*\d*\.?\d*', f'local_supplies={new_value}00', content)

        # Write the updated content back to the file
        file.seek(0)
        file.write(new_content)
        file.truncate()

def update_files_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            parse_and_update_file(file_path)
            print(f"Updated {filename}")

# Replace 'your_directory_path' with the path to the directory containing your .txt files
directory_path = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\history\states'
update_files_in_directory(directory_path)