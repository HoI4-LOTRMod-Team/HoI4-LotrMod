import os
import re

# ================= USER CONFIGURATION =================

# 1. The folder you want to search (use r"" to handle Windows backslashes correctly)
# Example: r"C:\Users\Name\Documents\MyGame"
ROOT_DIRECTORY = r"C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr"

# 2. The ID you want to find
SEARCH_STRING = "rhunexpanded.25"

# 3. The ID you want to replace it with
REPLACE_STRING = "rhun.29"

# 4. SAFETY SWITCH
# Set to False = Just print what would happen (Dry Run)
# Set to True  = Actually change the files
LIVE_MODE = True

# ======================================================

def run_replacement():
    # Construct the Regex Pattern
    # re.escape handles special chars like dots. 
    # r"(?!\d)" asserts the next character is NOT a digit.
    pattern_str = re.escape(SEARCH_STRING) + r"(?!\d)"
    pattern = re.compile(pattern_str)

    print(f"--- Starting ---")
    print(f"Directory: {ROOT_DIRECTORY}")
    print(f"Pattern:   '{SEARCH_STRING}' (ignoring larger numbers like {SEARCH_STRING}9)")
    print(f"Replace:   '{REPLACE_STRING}'")
    print(f"Mode:      {'LIVE (Writing changes)' if LIVE_MODE else 'DRY RUN (Read-only)'}")
    print(f"----------------\n")

    files_modified = 0
    total_occurrences = 0

    # Walk through the directory tree
    for dirpath, _, filenames in os.walk(ROOT_DIRECTORY):
        for filename in filenames:
            if filename.lower().endswith(('.txt', '.yml', '.yaml')):
                filepath = os.path.join(dirpath, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count matches to see if we need to do anything
                    matches = len(pattern.findall(content))
                    
                    if matches > 0:
                        # Perform replacement in memory
                        new_content = pattern.sub(REPLACE_STRING, content)
                        
                        print(f"[{'FIXED' if LIVE_MODE else 'FOUND'}] {filepath} ({matches} hits)")
                        
                        if LIVE_MODE:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                        
                        files_modified += 1
                        total_occurrences += matches

                except UnicodeDecodeError:
                    print(f"[SKIP] Encoding error in file: {filename}")
                except Exception as e:
                    print(f"[ERROR] {filepath}: {e}")

    print(f"\nFinished! Files touched: {files_modified}. Total replacements: {total_occurrences}.")

if __name__ == "__main__":
    run_replacement()