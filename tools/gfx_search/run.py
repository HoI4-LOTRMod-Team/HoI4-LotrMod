from subscripts import settingsreader
from subscripts import gfxparser
from subscripts import imageconverter
from subscripts import templatebuilder
import os

settings = settingsreader.read_json("tools/gfx_search/settings.json")

for cat_str in settings["categories"]:
    cat = settings["categories"][cat_str]
    name = cat["name"]
    gfx_file = cat["gfx_file"]
    img_size_x = cat["img_size_x"]
    img_size_y = cat["img_size_y"]

    # Parse GFX file, get list of GFX_entries and filepaths
    gfx_entries = gfxparser.parse_gfx_file(gfx_file)

    # For each entry, convert to PNG and generate a <div>
    # Ensure the output directory exists
    output_directory = 'tools/gfx_search/images'
    os.makedirs(output_directory, exist_ok=True)
    image_divs = ""
    for (gfx, file) in gfx_entries:
        imageconverter.convert_to_png(file, output_directory+"/"+gfx+".png")
        image_divs += "\n<div class=\"image-item img-thumbnail\"><img src=\""+output_directory+"/"+gfx+".png"+"\"  loading=\"lazy\" alt=\""+gfx+"\"></div>"

    # Insert all the <div>s into a template
    templatebuilder.write_template("tools/gfx_search/test_template.html", "tools/gfx_search/test_out.html",
        {
            "$IMAGE_LIST_TOKEN$": image_divs
        }
    )