from wand.image import Image
import os

# Input and output folders
input_folder = 'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\event_pictures\news_events\news_events_unmasked'  # Replace with your input folder path
output_folder = 'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\event_pictures\news_events\news_events_unmasked'  # Replace with your output folder path

# Desired dimensions
new_width = 512  # Replace with your desired width
new_height = 512  # Replace with your desired height

# Make sure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# List all .tga files in the input folder
tga_files = [f for f in os.listdir(input_folder) if f.endswith('.tga')]

# Process each .tga file
for tga_file in tga_files:
    # Open the TGA image using Wand
    with Image(filename=os.path.join(input_folder, tga_file)) as img:
        # Resize the image
        img.resize(new_width, new_height)

        # Save the resized image as DDS
        img.format = 'dds'
        img.save(filename=os.path.join(output_folder, os.path.splitext(tga_file)[0] + '.dds'))

print("Conversion complete.")