from subscripts import settingsreader
from subscripts import gfxparser
from subscripts import docsparser
from subscripts import imageconverter
from subscripts import templatebuilder
import os

settings = settingsreader.read_json("tools/gfx_search/settings.json")

# Get a list of all categories
cat_list = settings["categories"]

# Keep a list of all images, so that we can clean up afterwards
all_images_list = []

def proc_image_category(cat_str, cat, settings):
    global all_images_list

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
        converted = imageconverter.convert_to_png(file, output_directory+"/"+gfx+".png")

        image_divs += "\n<div class=\"image-item img-thumbnail search-list-entry\" copy-to-clipboard-data=\""+gfx+"\" search-list-data=\""+gfx+"\"><img src=\"images/"+cat_str+"/"+gfx+".png"+"\"  loading=\"lazy\" alt=\""+gfx+"\"></div>"
        all_images_list += output_directory+"/"+gfx+".png"

    # Insert all elements into a template
    templatebuilder.write_template("tools/gfx_search/templates/gfx_search_category_template.html", "tools/gfx_search/"+cat_str+".html",
        {
            "$IMAGE_LIST_TOKEN$": image_divs,
            "$NAV_BAR_TOKEN$": nav_bar,
            "$ITEM_SIZE_X_TOKEN$": str(img_size_x),
            "$ITEM_SIZE_Y_TOKEN$": str(img_size_y),
            "$CATEGORY_NAME_TOKEN$": str(name)
        }
    )

def proc_docs_category(cat_str, cat, settings):
    name = cat["name"]
    docs_directory = cat["docs_directory"]
    img_size_x = cat["img_size_x"]
    img_size_y = cat["img_size_y"]

    # Create list of categoy button-links
    nav_bar = ""
    for c in cat_list:
        if c == cat_str:
            nav_bar += "<a href=\""+c+".html\" role=\"button\" class=\"btn btn-secondary\">"+settings["categories"][c]["name"]+"</a>"
        else:
            nav_bar += "<a href=\""+c+".html\" role=\"button\" class=\"btn btn-outline-secondary\">"+settings["categories"][c]["name"]+"</a>"

    doc_divs = ""
    txt_files = [file for file in os.listdir(docs_directory) if file.endswith('.txt')]
    for txt_file in txt_files:
        file_path = os.path.join(docs_directory, txt_file)
        doc_entries = docsparser.extract_docs_info(file_path)

        for (f_name, f_cat, f_desc) in doc_entries:
            doc_divs += "\n<div class=\"text-item img-thumbnail search-list-entry\"  copy-to-clipboard-data=\""+f_name+"\" search-list-data=\""+f_name+" "+f_desc+"\"><code>"+f_name+"</code><br>"+f_desc+"<div class = \"alignright\">("+f_cat+")</div></div>"

    # Insert all elements into a template
    templatebuilder.write_template("tools/gfx_search/templates/gfx_search_category_template.html", "tools/gfx_search/"+cat_str+".html",
        {
            "$IMAGE_LIST_TOKEN$": doc_divs,
            "$NAV_BAR_TOKEN$": nav_bar,
            "$ITEM_SIZE_X_TOKEN$": str(img_size_x),
            "$ITEM_SIZE_Y_TOKEN$": str(img_size_y),
            "$CATEGORY_NAME_TOKEN$": str(name)
        }
    )


# Process eahc category individually
for cat_str in settings["categories"]:
    print("Processing: "+cat_str)

    cat = settings["categories"][cat_str]
    if("is_docs" in cat and cat["is_docs"]):
        proc_docs_category(cat_str, cat, settings)
    else:
        proc_image_category(cat_str, cat, settings)

# Clean up all the images that we don't use
directory_path = 'relative/path/to/your/directory'
full_directory_path = os.path.join(os.getcwd(), "tools/gfx_search/images/")
unusued_images_count = 0

# Get a list of PNG files in the directory
png_files = [os.path.join(full_directory_path, file) for file in os.listdir(full_directory_path) if file.lower().endswith('.png') and os.path.isfile(os.path.join(full_directory_path, file))]

# Iterate over the PNG files and remove those that are not in images_list
for file_path in png_files:
    if file_path not in all_images_list:
        os.remove(file_path)
        unusued_images_count += 1
        #print(f"PNG file '{file_path}' removed.")
print("Removed "+str(unusued_images_count)+" unused images.")