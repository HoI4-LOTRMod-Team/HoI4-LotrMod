import os
from PIL import Image

def process_dds_files(directory):
    # Loop through all files in the given directory
    for filename in os.listdir(directory):
        if filename.endswith(".dds"):
            filepath = os.path.join(directory, filename)

            # Open the image using PIL
            with Image.open(filepath) as img:
                width, height = img.size

                # Check if the width is even; if not, skip this image
                if width % 2 != 0:
                    print(f"Skipping {filename}, width is not even.")
                    continue

                # Crop the left half of the image
                left_half = img.crop((0, 0, width // 2, height))

                # Create a new image of the same size as the original
                new_img = Image.new("RGBA", (width, height))

                # Paste the left half twice (side by side) into the new image
                new_img.paste(left_half, (0, 0))
                new_img.paste(left_half, (width // 2, 0))

                # Save the new image, overwriting the original file
                new_img.save(filepath)

                print(f"Processed and saved {filename}")

# Specify the directory containing the .dds files
directory = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\interface\counters\divisions_small'

# Run the processing function
process_dds_files(directory)
