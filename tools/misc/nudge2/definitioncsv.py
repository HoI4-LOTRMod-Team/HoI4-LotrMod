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

    for st in states:
        col = random_color()
        for prov in st.province_list:
            csv[prov][13] = st.state_id
            csv[prov][14] = col
            csv[prov][17] = st.is_impassable
            csv[prov][18] = impassable_colormap[st.is_impassable]

    for st in regions:
        col = random_color()
        for prov in st.province_list:
            csv[prov][15] = st.region_id
            csv[prov][16] = col

    return csv






