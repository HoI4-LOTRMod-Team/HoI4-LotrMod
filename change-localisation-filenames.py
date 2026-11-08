import os

#first copy paste the english folder in "/localisation/english" and then rename that folder to the language 
#you want to translate in (for example, spanish or russian) then change the other parts in this script to the desired new language-
#Then run this script with "python3 change-localisation-filenames.py" in the root folder of this project

def rename_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if "_l_english" in file:
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, file.replace("_l_english", "_l_german")) #change "_l_german" to your new language, for example "_l_spanish"
                os.rename(old_path, new_path)
                print(f'Renamed: {old_path} -> {new_path}')

if __name__ == "__main__":
    base_folder = "FULL_PATH_TO_LOCALISATION_FOLDER/localisation"  # Replace with the actual path to your "localisation" folder
    english_folder = os.path.join(base_folder, "english") #original english base names (copy english folder, rename it to the new language you want to translate)
    new_lang_folder = os.path.join(base_folder, "german") #paste the new language here (for example german, spanish or anything else)

    # Rename files directly in the "german" or any other  folder
    rename_files(new_lang_folder)

    # Rename files in subfolders of "german" (or your selected language)
    for folder in os.listdir(new_lang_folder):
        folder_path = os.path.join(new_lang_folder, folder)
        if os.path.isdir(folder_path):
            rename_files(folder_path)
