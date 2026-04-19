import os
import math
from pathlib import Path
from PIL import Image

def pad_dds_images(directory_path):
    # Convert string to Path object for easy directory traversal
    base_dir = Path(directory_path)
    
    # Find all .dds files in this directory and all subdirectories
    dds_files = list(base_dir.rglob('*.dds'))
    
    if not dds_files:
        print(f"No .dds files found in {directory_path}")
        return

    print(f"Found {len(dds_files)} .dds files. Checking dimensions...")

    for filepath in dds_files:
        try:
            with Image.open(filepath) as img:
                w, h = img.size
                
                # Check if dimensions are already multiples of 4
                if w % 4 == 0 and h % 4 == 0:
                    continue 

                # Calculate new dimensions (round up to the nearest multiple of 4)
                new_w = math.ceil(w / 4) * 4
                new_h = math.ceil(h / 4) * 4
                
                # Calculate total padding needed
                pad_x = new_w - w
                pad_y = new_h - h
                
                # Calculate left and top padding. 
                # math.ceil() ensures the alternating logic (left gets the extra pixel if pad_x is odd)
                pad_left = math.ceil(pad_x / 2)
                pad_top = math.ceil(pad_y / 2)
                
                # Convert original image to RGBA to ensure it supports transparency
                img_rgba = img.convert("RGBA")
                
                # Create a new blank, completely transparent image of the new size
                new_img = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
                
                # Paste the original image onto the transparent canvas at the calculated offsets
                new_img.paste(img_rgba, (pad_left, pad_top))
                
                # Save the image, overwriting the original file
                new_img.save(filepath, format="DDS")
                print(f"Resized {filepath.name}: {w}x{h} -> {new_w}x{new_h} (Added L:{pad_left}, R:{pad_x - pad_left}, T:{pad_top}, B:{pad_y - pad_top})")
                
        except Exception as e:
            print(f"Error processing {filepath.name}: {e}")

if __name__ == "__main__":
    # Replace this with the path to your folder, or use '.' for the current directory
    TARGET_DIRECTORY = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\interface\goals'
    pad_dds_images(TARGET_DIRECTORY)