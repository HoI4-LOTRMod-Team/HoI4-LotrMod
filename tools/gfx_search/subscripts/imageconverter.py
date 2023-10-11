from wand.image import Image

def convert_to_png(file_in, file_out):
    # Open the image using Wand and convert it to PNG format
    try:
        with Image(filename=file_in) as img:
            img.save(filename=file_out)
    except Exception as e:
        print(f'Error: {e}')
