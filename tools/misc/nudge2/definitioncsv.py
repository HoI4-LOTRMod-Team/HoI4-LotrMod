import csv
import random

from pdx_parser import *

from state import *


BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve() # Points at the lotr/ directory
DEFINITION_CSV_PATH = BASE_PATH / "map/definition.csv"

TERRAIN_PATH = BASE_PATH / "common/terrain/00_terrain.txt"



def get_terrain_colormap():
    obj = ParseListFromFile_asPObj(TERRAIN_PATH)
    cats = obj.Get("categories").value

    color_map = {}
    for cat in cats:
        col = cat.Get("color").value
        color_map[cat.id] = (int(col[0].value), int(col[1].value), int(col[2].value))

    return color_map


type_colormap = {
    "land": (255, 128, 128),
    "sea": (0, 0, 128),
    "lake": (128, 128, 255)
}


coastal_colormap = {
    True: (255, 255, 255),
    False: (0, 0, 0),
}

impassable_colormap = {
    True: (255, 128, 128),
    False: (128, 128, 128),
}

continent_colormap = {
    0: (0, 0, 0),       # Black
    1: (0, 0, 128),     # Navy
    2: (0, 128, 0),     # Green
    3: (0, 128, 128),   # Teal
    4: (128, 0, 0),     # Maroon
    5: (128, 0, 128),   # Purple
    6: (128, 128, 0),   # Olive
    7: (192, 192, 192), # Silver
    8: (128, 128, 128), # Gray
    9: (0, 0, 255),     # Blue
    10: (0, 255, 0),    # Lime
    11: (0, 255, 255),  # Aqua / Cyan
    12: (255, 0, 0),    # Red
    13: (255, 0, 255),  # Fuchsia / Magenta
    14: (255, 255, 0),  # Yellow
    15: (255, 255, 255) # White
}



def get_definition_csv():
    ret = []

    # Open the file
    with open(DEFINITION_CSV_PATH, 'r', newline='') as file:
        # Create a reader object
        reader = csv.reader(file, delimiter=';')
        
        # Loop over the rows
        for row in reader:
            ret.append(
                [
                    int(row[0]),    # id
                    int(row[1]),    # r
                    int(row[2]),    # g
                    int(row[3]),    # b
                    row[4],         # land
                    row[5]=="true", # coastal
                    row[6],         # terrain
                    int(row[7]),    # continent
                ]
            )
    return ret


def get_existing_prov_colors():
    cols = []
    with open(DEFINITION_CSV_PATH, 'r', newline='') as file:
        # Create a reader object
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            cols.append((int(row[1]), int(row[2]), int(row[3])))

    return cols


def random_color():
    return tuple(random.randint(0, 255) for _ in range(3))

# Adds:
#   8: province-color
#   9: terrain-color
#  10: type-color
#  11: coastal-color
#  12: continent-color
#  13: state-id
#  14: state-color
#  15: strat-region-id
#  16: strat-region-color
#  17: impassable
#  18: impassable-color
#  19: victory points and buildings
def get_expanded_definition():

    csv = get_definition_csv()
    states = get_all_states()
    regions = get_all_stratregion()

    terrain_colormap = get_terrain_colormap()

    for row in csv:
        row.append((row[1], row[2], row[3]))
        row.append(terrain_colormap[row[6]])
        row.append(type_colormap[row[4]])
        row.append(coastal_colormap[row[5]])
        row.append(continent_colormap[row[7]])
        row.append((0,0,0))
        row.append((0,0,0))
        row.append((0,0,0))
        row.append((0,0,0))
        row.append((0,0,0))
        row.append((0,0,0))
        row.append(type_colormap[row[4]]) # using type for base for prov/build mode

    for st in states:
        col = random_color()
        for prov in st.province_list:
            csv[prov][13] = st.state_id
            csv[prov][14] = col
            csv[prov][17] = st.is_impassable
            csv[prov][18] = impassable_colormap[st.is_impassable]

            for vp in st.get_vp_list():
                csv[int(vp.value[0].value)][19] = (255, 0, 255)
            for bld in st.get_bld_list():
                if bld.id.isnumeric():
                    c = csv[int(bld.id)][19]
                    c = (255 if c[2]>254 else 0, 255, 0)
                    csv[int(bld.id)][19] = c

    for st in regions:
        col = random_color()
        for prov in st.province_list:
            csv[prov][15] = st.region_id
            csv[prov][16] = col

    return csv


cached_prov_type = "land"

def get_new_province_color(prov_type):
    """
    Returns a unique RGB tuple for a new province.
    """
    global cached_prov_type
    print(f"[Stub] Generating new color for: {prov_type}")
    # Return a random distinct color for testing
    cached_prov_type = prov_type
    cols = get_existing_prov_colors()
    while True:
        if prov_type == "land":
            new_col = (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255))
        else: 
            new_col = (random.randint(0, 128), random.randint(0, 128), random.randint(0, 200))
        if new_col not in cols:
            return new_col


def create_new_province_from(old_rgb_tuple, new_prov_color):
    """
    Called when the user starts painting over an old province with a 'New' color.
    """
    global cached_prov_type
    print(f"[Stub] CREATING NEW PROVINCE based on properties of color: {old_rgb_tuple}")

    csv = get_definition_csv()
    for row in csv:
        # Check if the RGB matches
        if row[1] == old_rgb_tuple[0] and row[2] == old_rgb_tuple[1] and row[3] == old_rgb_tuple[2]:
            
            # 1. construct the data string WITHOUT a leading or trailing newline first
            new_line_content = f"{len(csv)};{new_prov_color[0]};{new_prov_color[1]};{new_prov_color[2]};"
            new_line_content += f"{cached_prov_type};{row[5]};{row[6]};{row[7]}"

            # 2. Open in 'a+' (Append + Read) to check the file state
            with open(DEFINITION_CSV_PATH, 'a+') as file:
                file.seek(0, 2) # Move cursor to the very end of the file
                file_size = file.tell()
                
                # If file is not empty, check the last character
                if file_size > 0:
                    file.seek(file_size - 1) # Move back one character
                    last_char = file.read(1)
                    
                    # If the last char is NOT a newline, we must add one to separate our new entry
                    if last_char != '\n':
                        file.write('\n')
                
                # 3. Write the new line
                file.write(new_line_content)
                
            return

    assert(False) # This code should be unreachable


def update_province_properties(provinces, overwrite_data):
    # 1. Read everything into memory
    with open(DEFINITION_CSV_PATH, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        data = list(reader) # Loads whole file into a list of lists

    # 2. Modify the specific lines
    for prov in provinces:
        if "type" in overwrite_data.keys(): data[prov][4] = overwrite_data["type"]
        if "coastal" in overwrite_data.keys(): data[prov][5] = overwrite_data["coastal"]
        if "terrain" in overwrite_data.keys(): data[prov][6] = overwrite_data["terrain"]
        if "continent" in overwrite_data.keys(): data[prov][7] = overwrite_data["continent"]

    # 3. Write everything back
    with open(DEFINITION_CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(data)

    print("Modified provinces: " + str(provinces) + " with values: " + str(overwrite_data))






