from wand.image import Image
import os

dir = r'C:\Users\kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\leaders\MOR'

# Get all .dds files in the current directory
dds_files = [dir+"\\"+file for file in os.listdir(dir) if file.endswith('.dds')]

# Loop over each .dds file and re-save it (overwrite the original file)
for dds_file in dds_files:
    # Open the DDS file using Wand
    try:
        with Image(filename=dds_file) as img:
            # Re-save the image in DDS format (overwrite the original file)
            img.save(filename=dds_file)
            print(f"File '{dds_file}' re-saved.")
    except Exception as e:
        print(f"Error processing '{dds_file}': {e}")
