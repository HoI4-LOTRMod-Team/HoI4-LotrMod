import os

def modify_files(numbers, directory_path, your_string):
    # Ensure the directory path ends with a '/'
    if not directory_path.endswith('/'):
        directory_path += '/'
    
    # List all files in the directory
    files = os.listdir(directory_path)
    
    # Filter files that start with one of the numbers followed by a minus sign
    relevant_files = [f for f in files for number in numbers if f.startswith(f"{number}-")]
    
    for file_name in relevant_files:
        file_path = directory_path + file_name
        with open(file_path, 'r+') as file:
            content = file.read()
            
            # Find the 'provinces={...}' part and add your string after it
            closing_bracket_index = content.find('}')
            if closing_bracket_index != -1:
                # Add a new line and your string after the closing bracket
                new_content = content[:closing_bracket_index+1] + '\n' + your_string + content[closing_bracket_index+1:]
                
                # Go back to the beginning of the file to overwrite it
                file.seek(0)
                file.write(new_content)
                file.truncate()  # Truncate the file in case new content is shorter than old

if __name__ == "__main__":
    numbers = ['106', '98', '104', '127', '99', '128', '124', '118', '117']
    directory_path = r'C:\Users\kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\strategicregions'  # Adjust this path
    your_string = r'	naval_terrain=water_fjords'  # The string you want to add
    
    modify_files(numbers, directory_path, your_string)