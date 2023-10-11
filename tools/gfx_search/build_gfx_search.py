import re
import os
from wand.image import Image

# Define the function that will be called with name and texturefile values
def process_sprite(name, texturefile):
    #print(f"Processing sprite: Name={name}, Texturefile={texturefile}")
    new_img = convert_image("C:/Users/kahl/helliaca/HoI4-LotrMod/"+texturefile)
    return "<div class=\"image-item img-thumbnail\"><img src=\"images/"+new_img+"\"  loading=\"lazy\" alt=\""+name+"\"></div>"

def convert_image(path):
    # Ensure the output directory exists
    output_directory = 'images'
    os.makedirs(output_directory, exist_ok=True)

    # Open the image using Wand and convert it to PNG format
    try:
        with Image(filename=path) as img:
            # Get the file name (without extension) from the original path
            filename = os.path.splitext(os.path.basename(path))[0]
            # Save the image as PNG in the /images subdirectory
            output_path = os.path.join(output_directory, f'{filename}.png')
            img.save(filename=output_path)
            print(f'Image converted and saved as: {output_path}')
            # Return the filename of the new image
            return f'{filename}.png'
    except Exception as e:
        print(f'Error: {e}')
        return None

def write_website(content):
    with open('test_template.html', 'r') as template:
        t = template.read()
        t = t.replace("<!-- IMAGE_INSERT_TOKEN -->", content)
        
        f = open("test_2.html", "w")
        f.write(t)
        f.close()


# Read the file and extract sprite entries
with open('C:/Users/kahl/helliaca/HoI4-LotrMod/interface/auto_generated/spirits.gfx', 'r') as file:
    content = file.read()

# Extract sprite entries using regular expressions
sprite_entries = re.findall(r'spriteType = \{\s+name = "(.*?)".+?texturefile = "(.*?)".+?\}', content, re.DOTALL)

# Process each sprite entry
output = ""
for name, texturefile in sprite_entries:
    output = output + "\n" + process_sprite(name, texturefile)
    
write_website(output)
