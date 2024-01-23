#from wand.image import Image
import os
from glob import glob
from PIL import Image

# Define the directories
base_dir = '../gfx/flags/'
medium_dir = os.path.join(base_dir, 'medium/')
small_dir = os.path.join(base_dir, 'small/')

# Define the sizes for medium and small
large_size = (82, 52)
medium_size = (41, 26)
small_size = (10, 7)

# Function to resize and save the image using Pillow
def resize_and_save(image_path, output_dir, size, format='tga'):
    with Image.open(image_path) as img:
        img = img.resize(size, Image.Resampling.LANCZOS)
        output_file = os.path.splitext(os.path.basename(image_path))[0] + ('.' + format if format else '')
        output_path = os.path.join(output_dir, output_file)
        img.save(output_path)

# Read all *.tga files in the base directory
tga_files = glob(os.path.join(base_dir, '*.tga'))
png_files = glob(os.path.join(base_dir, '*.png'))

print("Checking for missing flags...")

# Process PNG files without corresponding TGA files
for png_file in png_files:
    tga_file = os.path.splitext(png_file)[0] + '.tga'
    if tga_file not in tga_files:
        print("Generating large flag for: "+png_file)
        resize_and_save(png_file, base_dir, large_size)

# Update the list of TGA files after processing PNGs
tga_files = glob(os.path.join(base_dir, '*.tga'))

for tga_file in tga_files:
    file_name = os.path.basename(tga_file)
    
    # Check if the file exists in medium and small directories
    medium_file = os.path.join(medium_dir, file_name)
    small_file = os.path.join(small_dir, file_name)
    
    if not os.path.exists(medium_file):
        print("Generating medium flag for: "+file_name)
        resize_and_save(tga_file, medium_dir, medium_size)
    
    if not os.path.exists(small_file):
        print("Generating small flag for: "+file_name)
        resize_and_save(tga_file, small_dir, small_size)
        
print("Done.")

