import os
import argparse

def search_files(directory, search_text, case_sensitive):
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.yml'):
                try:
                    with open(os.path.join(foldername, filename), 'r') as file:
                        for line in file:
                            if (case_sensitive and search_text in line) or (not case_sensitive and search_text.lower() in line.lower()):
                                print(line)
                except:
                    continue

search_files(f"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\localisation\english", "Railway Gun", False)