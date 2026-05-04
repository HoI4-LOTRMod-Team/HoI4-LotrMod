

from pdx_parser import *

from pathlib import Path





def process_file(file_path):
    """
    This is the function called for every .txt file found.
    Currently, it just prints the path.
    """
    #print(f"Processing: {file_path}")
    
    docs = ParseListFromFile_asPObj(file_path)

    for doc in docs.value:
        for rew in doc.Get("rewards").value:
            print(doc.id + "_" + rew.id)
        





def process_directory(directory_path):
    # Convert string path to a Path object
    root_dir = Path(directory_path)

    # Check if directory exists
    if not root_dir.exists():
        #print(f"Error: The path '{directory_path}' does not exist.")
        return

    # .rglob('*') searches recursively. 
    # '*.txt' filters for text files.
    for file_path in root_dir.rglob('*.txt'):
        process_file(file_path)



PATH = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\doctrines\subdoctrines'

process_directory(PATH)