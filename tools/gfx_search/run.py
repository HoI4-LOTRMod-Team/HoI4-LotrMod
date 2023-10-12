from subscripts import settingsreader
from subscripts import gfxparser
from subscripts import imageconverter
from subscripts import templatebuilder
import os

settings = settingsreader.read_json("tools/gfx_search/settings.json")

# Get a list of all categories
cat_list = settings["categories"]

# Process eahc category individually
for cat_str in settings["categories"]:
    print("Processing: "+cat_str)

    cat = settings["categories"][cat_str]
    name = cat["name"]
    gfx_file = cat["gfx_file"]
    img_size_x = cat["img_size_x"]
    img_size_y = cat["img_size_y"]

    # Create list of categoy button-links
    nav_bar = ""
    for c in cat_list:
        if c == cat_str:
            nav_bar += "<a href=\""+c+".html\" role=\"button\" class=\"btn btn-secondary\">"+settings["categories"][c]["name"]+"</a>"
        else:
            nav_bar += "<a href=\""+c+".html\" role=\"button\" class=\"btn btn-outline-secondary\">"+settings["categories"][c]["name"]+"</a>"

    # Parse GFX file, get list of GFX_entries and filepaths
    gfx_entries = gfxparser.parse_gfx_file(gfx_file)

    # For each entry, convert to PNG and generate a <div>
    # Ensure the output directory exists
    output_directory = "tools/gfx_search/images/"+cat_str
    os.makedirs(output_directory, exist_ok=True)
    image_divs = ""
    for (gfx, file) in gfx_entries:
        imageconverter.convert_to_png(file, output_directory+"/"+gfx+".png")
        image_divs += "\n<div class=\"image-item img-thumbnail\"><img src=\"images/"+cat_str+"/"+gfx+".png"+"\"  loading=\"lazy\" alt=\""+gfx+"\"></div>"

    # Insert all elements into a template
    templatebuilder.write_template("tools/gfx_search/test_template.html", "tools/gfx_search/"+cat_str+".html",
        {
            "$IMAGE_LIST_TOKEN$": image_divs,
            "$NAV_BAR_TOKEN$": nav_bar,
            "$ITEM_SIZE_X_TOKEN$": str(img_size_x),
            "$ITEM_SIZE_Y_TOKEN$": str(img_size_y),
            "$CATEGORY_NAME_TOKEN$": str(name)
        }
    )