import os
from wand.image import Image
from wand.color import Color

# Directory containing the .dds files
input_directory = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\interface\counters\division_templates_large'
output_directory = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\interface\counters\temp'

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Process each .dds file in the directory
for filename in os.listdir(input_directory):
    if filename.endswith('.dds'):
        file_path = os.path.join(input_directory, filename)
        
        with Image(filename=file_path) as img:
            # Ensure the image has an alpha channel to handle transparency
            img.alpha_channel = 'activate'

            # Trim the image to remove fully transparent borders
            img.trim()

            # Resize the image to a height of 17 pixels, keeping the aspect ratio
            img.resize(width=int(img.width * (17.0 / img.height)), height=17)

            # Save the modified image with transparency preserved
            output_file_path = os.path.join(output_directory, filename)
            img.save(filename=output_file_path)

print("Processing complete!")