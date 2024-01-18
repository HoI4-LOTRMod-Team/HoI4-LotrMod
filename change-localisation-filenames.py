import os

def rename_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if "_l_english" in file:
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, file.replace("_l_english", "_l_german"))
                os.rename(old_path, new_path)
                print(f'Renamed: {old_path} -> {new_path}')

if __name__ == "__main__":
    base_folder = "/localisation"  # Replace with the actual path to your "localisation" folder
    english_folder = os.path.join(base_folder, "english")
    german_folder = os.path.join(base_folder, "german")

    # Rename files directly in the "german" folder
    rename_files(german_folder)

    # Rename files in subfolders of "german"
    for folder in os.listdir(german_folder):
        folder_path = os.path.join(german_folder, folder)
        if os.path.isdir(folder_path):
            rename_files(folder_path)
