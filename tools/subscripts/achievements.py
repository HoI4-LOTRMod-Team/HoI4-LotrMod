from wand.image import Image
import os

def process_files(directory):
    # Define the suffixes
    grey_suffix = "_grey"
    not_eligible_suffix = "_not_eligible"
    
    # Load the crossout image
    with Image(filename=r'subscripts\res\crossout.png') as crossout_img:
        # Iterate through all .dds files in the given directory
        for filename in os.listdir(directory):
            if filename.endswith(".dds") and not filename.endswith(grey_suffix + ".dds") and not filename.endswith(not_eligible_suffix + ".dds"):
                # Construct the file path
                file_path = os.path.join(directory, filename)
                # Process the image
                with Image(filename=file_path) as img:
                    # Convert to black and white by setting saturation to 0
                    img.modulate(saturation=0)
                    # Save the grey image
                    grey_filename = filename.rsplit('.', 1)[0] + grey_suffix + '.dds'
                    grey_file_path = os.path.join(directory, grey_filename)
                    img.save(filename=grey_file_path)
                    
                    # Add the crossout image on top
                    img.composite(crossout_img, left=0, top=0)
                    # Save the not eligible image
                    not_eligible_filename = filename.rsplit('.', 1)[0] + not_eligible_suffix + '.dds'
                    not_eligible_file_path = os.path.join(directory, not_eligible_filename)
                    img.save(filename=not_eligible_file_path)

if __name__ == "__main__":
    directory = r'..\gfx\achievements'
    process_files(directory)