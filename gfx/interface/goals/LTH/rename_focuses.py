import os
import re

# Get .dds files with less than two underscores in the current directory
dds_files = [file for file in os.listdir() if file.endswith('.dds') and file.count('_') < 2]

# Specify the directory to replace instances
replace_directory = '/path/to/your/directory'  # Replace this with the actual directory path

# Loop over each .dds file
for dds_file in dds_files:
    # Output the file name to console
    print(f"Current file: {dds_file}")
    
    # Await input for new file name
    new_name = input("Enter new name (without .dds extension): ").strip()
    
    # Rename the file
    os.rename(dds_file, new_name + '.dds')
    
    # Loop through files in the specified directory
    for root, dirs, files in os.walk(replace_directory):
        for file in files:
            # Read file content
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Replace instances of GFX_goal_[filename-without-dds]
            pattern = r'GFX_goal_' + re.escape(os.path.splitext(dds_file)[0])
            new_pattern = r'GFX_goal_' + new_name
            updated_content = re.sub(pattern, new_pattern, file_content)
            
            # Write updated content back to the file
            with open(os.path.join(root, file), 'w', encoding='utf-8') as f:
                f.write(updated_content)

    print(f"File '{dds_file}' renamed to '{new_name}.dds' and instances replaced in '{replace_directory}' directory.")
