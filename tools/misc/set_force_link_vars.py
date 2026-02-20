import os
import re

# Set the path to your directory here
# Use "." for the current folder where the script is located
DIRECTORY = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\history\states' 

def update_files():
    # Pattern to find the ID
    ownership_pattern = re.compile(r'force_link_ownership_to\s*=\s*(\d+)')
    # Pattern to find the history block start
    history_pattern = re.compile(r'history\s*=\s*\{')

    for filename in os.listdir(DIRECTORY):
        if filename.endswith(".txt"):
            filepath = os.path.join(DIRECTORY, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find the ID (e.g., 123)
            match = ownership_pattern.search(content)
            
            if match:
                link_id = match.group(1)
                new_line = f"\n\t\tset_variable = {{ force_linked_to = {link_id} }}"
                
                # Check if we have a history block to inject into
                if "history = {" in content:
                    # We replace the first occurrence of 'history = {' 
                    # with itself + the new variable line
                    updated_content = history_pattern.sub(f"history = {{{new_line}", content, count=1)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    print(f"Updated: {filename} with ID {link_id}")
                else:
                    print(f"Skipped: {filename} (ID found, but no 'history = {{' block)")

if __name__ == "__main__":
    update_files()
    print("Done!")