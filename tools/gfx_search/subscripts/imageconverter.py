from wand.image import Image
import os

def convert_to_png(file_in, file_out):
    if os.path.exists(file_out):
        if get_image_hash(file_in) == get_image_hash(file_out):
            return False

    # Open the image using Wand and convert it to PNG format
    try:
        with Image(filename=file_in) as img:
            img.save(filename=file_out)
            return True
    except Exception as e:
        print(f'Error: {e}')
        return False


def get_image_hash(image_path):
    with Image(filename=image_path) as img:
        # Get the perceptual hash of the image
        perceptual_hash = img.signature
        return perceptual_hash


