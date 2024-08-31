import os
from wand.image import Image
from wand.color import Color

# Directory containing .dds files
input_directory = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\interface\counters\temp'
# Alpha threshold (0-255)
alpha_threshold = 128

# Iterate through all files in the directory
for filename in os.listdir(input_directory):
    if filename.endswith('.dds'):
        file_path = os.path.join(input_directory, filename)
        
        with Image(filename=file_path) as img:
            # Ensure the image has an alpha channel
            img.alpha_channel = True
            
            # Iterate through each pixel
            width, height = img.size
            with img.clone() as clone_img:
                for y in range(height):
                    for x in range(width):
                        # Get pixel's alpha value
                        pixel = clone_img[x, y]
                        alpha = pixel.alpha_int8
                        green = pixel.green_int8
                        
                        # If alpha is below the threshold, set it to 0
                        if alpha < alpha_threshold or green < 38:
                            clone_img[x, y] = Color('transparent')

                # Save the modified image
                clone_img.save(filename=file_path)

        print(f"Processed {filename}")
