import re

def parse_gfx_file(gfx_file_path):
    with open(gfx_file_path, 'r') as file:
        content = file.read()

        # Extract sprite entries using regular expressions
        sprite_entries = re.findall(r'spriteType = \{\s+name = "(.*?)".+?texturefile = "(.*?)".+?\}', content, re.DOTALL)

        return sprite_entries
