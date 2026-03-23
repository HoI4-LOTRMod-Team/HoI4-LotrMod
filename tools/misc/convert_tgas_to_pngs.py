import os
import glob
from PIL import Image

# Hard-coded path to your directory containing the TGA files
directory_path = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\flags'

# Create the search pattern for all .tga files
search_pattern = os.path.join(directory_path, "*.tga")
tga_files = glob.glob(search_pattern)

if not tga_files:
    print(f"No .tga files found in {directory_path}")
else:
    print(f"Found {len(tga_files)} .tga files. Starting conversion...")
    
    for tga_file in tga_files:
        try:
            # Open the TGA image
            with Image.open(tga_file) as img:
                # Get the filename without the extension
                base_name = os.path.splitext(tga_file)[0]
                
                # Create the new PNG path
                png_file = f"{base_name}.png"
                
                # Save it out as a PNG
                img.save(png_file, "PNG")
                print(f"Converted: {os.path.basename(png_file)}")
                
        except Exception as e:
            print(f"Failed to convert {os.path.basename(tga_file)}. Error: {e}")

    print("All done!")