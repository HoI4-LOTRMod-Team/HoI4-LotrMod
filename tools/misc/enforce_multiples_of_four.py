import os
from pathlib import Path
from wand.image import Image
from wand.color import Color

def pad_dds_files(target_directory="."):
    """
    Recursively finds all .dds files in the target directory and pads them 
    with transparent pixels so both dimensions are multiples of 4.
    """
    # Use pathlib to recursively find all .dds files
    dds_files = list(Path(target_directory).rglob('*.dds'))
    
    if not dds_files:
        print(f"No .dds files found in {target_directory} or its subdirectories.")
        return

    print(f"Found {len(dds_files)} .dds file(s). Processing...")

    for filepath in dds_files:
        try:
            with Image(filename=str(filepath)) as img:
                original_w, original_h = img.width, img.height
                
                # Calculate the next multiple of 4
                target_w = ((original_w + 3) // 4) * 4
                target_h = ((original_h + 3) // 4) * 4
                
                # If dimensions are already multiples of 4, skip
                if original_w == target_w and original_h == target_h:
                    continue
                
                # Calculate how many total pixels need to be added
                delta_w = target_w - original_w
                delta_h = target_h - original_h
                
                # To alternate left/right and top/bottom, we divide by 2.
                # Adding 1 before floor division ensures that if we need an odd amount 
                # of padding (e.g., 3), the left/top gets 2 and the right/bottom gets 1.
                left_pad = (delta_w + 1) // 2
                top_pad = (delta_h + 1) // 2
                
                print(f"Padding {filepath.name}: {original_w}x{original_h} -> {target_w}x{target_h}")
                
                # Set the background to transparent before expanding the canvas
                img.background_color = Color('transparent')
                
                # Expand the image canvas.
                # A negative x/y offsets the original image on the new canvas,
                # effectively pushing it to the right/down by our padding amounts.
                img.extent(width=target_w, height=target_h, x=-left_pad, y=-top_pad)
                
                # Save the image, overwriting the original
                img.save(filename=str(filepath))
                
        except Exception as e:
            print(f"Error processing {filepath.name}: {e}")

    print("Processing complete.")

if __name__ == "__main__":
    # You can change "." to a specific directory path like r"C:\Your\Path\Here"
    directory_to_scan = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\interface\goals'
    pad_dds_files(directory_to_scan)