import os
from PIL import Image
import pydirectx.dds

def process_dds_image(file_path, alpha_threshold=128):
    # Load the image
    dds_image = pydirectx.dds.load(file_path)

    # Convert the DDS image to RGBA mode
    image = Image.frombytes('RGBA', dds_image.size, dds_image.data)
    
    # Get the image data as a pixel array
    pixels = image.load()

    # Iterate through each pixel and modify alpha values below the threshold
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if a < alpha_threshold:
                pixels[x, y] = (r, g, b, 0)

    # Save the modified image back to the file
    dds_image = pydirectx.dds.save(image.tobytes(), image.size)
    with open(file_path, 'wb') as f:
        f.write(dds_image)

def process_all_dds_files(directory, alpha_threshold=128):
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.lower().endswith(".dds"):
            file_path = os.path.join(directory, filename)
            print(f"Processing {file_path}...")
            process_dds_image(file_path, alpha_threshold)
    print("Processing complete.")

if __name__ == "__main__":
    # Define the directory and alpha threshold
    directory = "./dds_files"  # Change to your directory
    alpha_threshold = 128  # Set your desired threshold
    
    # Process all DDS files in the directory
    process_all_dds_files(directory, alpha_threshold)
