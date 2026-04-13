import csv
import random
import heapq
import hashlib

from pdx_parser import *

from state import *

from pathlib import Path

from collections import deque


BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve() # Points at the lotr/ directory
DEFINITION_CSV_PATH = BASE_PATH / "map/definition.csv"

TERRAIN_PATH = BASE_PATH / "common/terrain/00_terrain.txt"

VPS_LOC_PATH = BASE_PATH / "localisation/english/victory_points_l_english.yml"



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

def get_color_from_seed(seed_str: str) -> tuple[int, int, int]:
    """
    Returns an RGB tuple based on a string seed.
    Enforces the max 3-byte input constraint.
    """
    # 1. Enforce max 3 bytes constraint (optional based on your needs)
    if len(seed_str.encode('utf-8')) > 3:
        raise ValueError("Seed string exceeds 3 bytes.")

    # 2. Hash the string (MD5 is fast and sufficient for non-security colors)
    # We encode to utf-8 to get bytes
    hash_object = hashlib.md5(seed_str.encode('utf-8'))
    
    # 3. Get the digest (bytes)
    hex_digest = hash_object.hexdigest()

    # 4. Convert the first 6 hex characters (3 bytes) into integers
    # R: chars 0-2, G: chars 2-4, B: chars 4-6
    r = int(hex_digest[0:2], 16)
    g = int(hex_digest[2:4], 16)
    b = int(hex_digest[4:6], 16)

    return (r, g, b)


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
#  20: owner country
#  21: owner country color
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
        row.append((0,0,0))
        row.append((0,0,0))

    for st in states:
        col = get_color_from_seed(str(st.state_id))
        ow_col = get_color_from_seed(st.owner)
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

            csv[prov][20] = st.owner
            csv[prov][21] = ow_col

    for st in regions:
        col = get_color_from_seed(str(st.region_id))
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


def create_new_province_from(old_rgb_tuple, new_prov_color=None):
    """
    Called when the user starts painting over an old province with a 'New' color.
    """
    global cached_prov_type
    print(f"[Stub] CREATING NEW PROVINCE based on properties of color: {old_rgb_tuple}")

    csv = get_definition_csv()
    for row in csv:
        # Check if the RGB matches
        if row[1] == old_rgb_tuple[0] and row[2] == old_rgb_tuple[1] and row[3] == old_rgb_tuple[2]:

            # generate new color if none was passed
            if new_prov_color is None:
                new_prov_color = get_new_province_color(row[4])
            
            # 1. construct the data string WITHOUT a leading or trailing newline first
            new_prov_id = len(csv)
            new_line_content = f"{new_prov_id};{new_prov_color[0]};{new_prov_color[1]};{new_prov_color[2]};"
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

            # fix state/stratregion by adding this province to the same as the OG
            old_prov_id = row[0]
            print(old_prov_id)

            # Only add to state if not a sea province
            if(cached_prov_type != "sea"):
                states = get_all_states()
                for st in states:
                    if old_prov_id in st.province_list:
                        st.province_list.append(new_prov_id)
                        st.province_list.sort()
                        st.apply_province_changes()
                        st.save_to_file()
                        break

            regions = get_all_stratregion()
            for st in regions:
                if old_prov_id in st.province_list:
                    st.province_list.append(new_prov_id)
                    st.province_list.sort()
                    st.apply_province_changes()
                    st.save_to_file()
                    break
                
            return

    assert(False) # This code should be unreachable


# geodesically splits a set of pixel coordinates
def split_pixels_geodesic(pixels, roughness=10.0):
    """
    Splits pixels into two sets with a jagged, organic boundary.
    
    Args:
        pixels: List of (x,y) tuples.
        roughness: How jagged the line should be. 
                   0.0 = Straight/Geometric.
                   Higher (e.g. 1.0 - 5.0) = More organic/wobbly.
    """
    if not pixels:
        return [], []

    pixel_set = set(pixels)
    
    # 1. Assign "Friction" to every pixel
    # This creates the "rough terrain". The path will wiggle to find the easy spots.
    # Base cost is 1.0, plus random noise.
    weights = {p: 1.0 + random.random() * roughness for p in pixels}

    # Build adjacency (4-way connectivity)
    neighbors = {p: [] for p in pixels}
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for x, y in pixels:
        for dx, dy in directions:
            n = (x + dx, y + dy)
            if n in pixel_set:
                neighbors[(x, y)].append(n)

    # Helper: Dijkstra's Algorithm (Weighted Shortest Path)
    def get_weighted_distances(start_node):
        # Priority Queue: stores (current_cost, pixel)
        pq = [(0.0, start_node)]
        distances = {start_node: 0.0}
        farthest_node = start_node
        max_dist = 0.0

        while pq:
            current_dist, current_node = heapq.heappop(pq)

            # If we found a shorter way to this node already, skip
            if current_dist > distances.get(current_node, float('inf')):
                continue

            # Track diameter logic
            if current_dist > max_dist:
                max_dist = current_dist
                farthest_node = current_node

            for neighbor in neighbors[current_node]:
                # Cost to step onto the neighbor
                move_cost = weights[neighbor]
                new_dist = current_dist + move_cost

                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))
        
        return distances, farthest_node

    # 2. Find endpoints (Using standard BFS distance first to find "true" ends quickly)
    # We do a quick unweighted pass just to find the tips of the bean, 
    # so the roughness doesn't mess up our diameter finding.
    from collections import deque
    def get_bfs_farthest(start):
        q = deque([start])
        seen = {start}
        last = start
        while q:
            last = q.popleft()
            for dx, dy in directions:
                n = (last[0]+dx, last[1]+dy)
                if n in pixel_set and n not in seen:
                    seen.add(n)
                    q.append(n)
        return last

    # Find the geometric tips of the shape
    tip_a = get_bfs_farthest(pixels[0])
    tip_b = get_bfs_farthest(tip_a)

    # 3. Run the "Race" through the rough terrain
    dists_a, _ = get_weighted_distances(tip_a)
    dists_b, _ = get_weighted_distances(tip_b)

    # 4. Split
    set_1 = []
    set_2 = []
    
    for p in pixels:
        # Get distances (default to infinity if unreachable, though shouldn't happen)
        da = dists_a.get(p, float('inf'))
        db = dists_b.get(p, float('inf'))
        
        if da < db:
            set_1.append(p)
        else:
            set_2.append(p)

    return set_1, set_2

def get_prov_color_from_id(id):
    csv = get_definition_csv()
    for row in csv:
        if row[0] == id:
            return ((row[1], row[2], row[3]))
    assert(False)



def set_prov_props(provinces, overwrite_data):
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


def get_prov_props(selected_provinces):
    """
    Analyzes selected provinces and returns a dictionary.
    
    - 'type', 'coastal', 'terrain', 'continent' return as dictionary keys.
    - 'state', 'region', 'impassable' are appended to the 'info' text.
    """
    definition = get_expanded_definition()
    
    if not selected_provinces:
        return {"info": "No provinces selected."}

    # Configuration: (Column Index, Label, Destination)
    # Destination: 'dict' = key in return object, 'info' = append to info string
    prop_config = [
        (4, "type", "dict"),
        (5, "coastal", "dict"),
        (6, "terrain", "dict"),
        (7, "continent", "dict"),
        (13, "state", "info"),
        (15, "region", "info"),
        (17, "impassable", "info")
    ]

    # 1. Calculate values for all properties
    calculated_props = {}
    
    for col_index, label, dest in prop_config:
        values = set()
        for prov_idx in selected_provinces:
            if 0 <= prov_idx < len(definition):
                values.add(definition[prov_idx][col_index])
        
        # Determine uniformity
        if len(values) == 1:
            val = list(values)[0]
            # Convert booleans or numbers to nice strings if necessary
            final_value = str(val) 
        elif len(values) > 1:
            final_value = "-- mixed --"
        else:
            final_value = "N/A"
            
        calculated_props[label] = (final_value, dest)

    # 2. Build the 'info' string
    count = len(selected_provinces)
    
    # Basic info
    info_lines = [
        f"Selection Count: {count}",
        f"Selection: {selected_provinces}",
        "---" # Visual separator
    ]
    
    # Add the specific properties requested for the info block
    for label, (val, dest) in calculated_props.items():
        if dest == "info":
            # Capitalize label for display (e.g., "state" -> "State")
            info_lines.append(f"{label.capitalize()}: {val}")

    # 3. Construct final dictionary
    result = {
        "info": "\n".join(info_lines)
    }

    # Add the remaining properties as dictionary keys
    for label, (val, dest) in calculated_props.items():
        if dest == "dict":
            result[label] = val

    return result


def set_state_props(provinces, overwrite_data):
    if len(provinces) < 1:
        return {"info": "No provinces selected."}
    
    states = get_all_states()
    loc = LocFile(STATES_LOC_DIR)

    for st in states:
        if provinces[0] in st.province_list:
            rename = None

            if "impassable" in overwrite_data.keys():
                if st.pObj.Has("impassable"): st.pObj.Remove("impassable")
                if overwrite_data["impassable"] == "yes":
                    st.pObj.Insert("impassable = yes")
            if "name" in overwrite_data.keys():
                loc.set(str(st.pObj.Get("name").value).replace('"', ''), overwrite_data["name"])
                loc.save(STATES_LOC_DIR)
                rename = str(st.state_id) + "-" + overwrite_data["name"] + ".txt"
            if "state_category" in overwrite_data.keys():
                if st.pObj.Has("state_category"):
                    st.pObj.Get("state_category").value = overwrite_data["state_category"]
                else:
                    st.pObj.Insert("state_category = " + overwrite_data["state_category"])
            st.save_to_file()
            if rename is not None:
                og_path = Path(st.filepath)
                new_path = og_path.with_name(rename)
                og_path.rename(new_path)


def get_state_props(provinces):
    if len(provinces) < 1:
        return {"info": "No provinces selected."}

    states = get_all_states()
    loc = LocFile(STATES_LOC_DIR)
    for st in states:
        if provinces[0] in st.province_list:
            ret = {}
            ret["impassable"] = "yes" if st.is_impassable else "no"
            ret["name"] = loc.get(str(st.pObj.Get("name").value).replace('"', ''))
            ret["state_category"] = str(st.pObj.Get("state_category").value)

            ret["info"] = f"ID: {st.state_id}"
            
            return ret

    assert(False)


def get_victory_points(provinces):
    locs = LocFile(VPS_LOC_PATH)
    vps = []
    states = get_all_states()
    for st in states:
        for vp in st.get_vp_list():
            prov_id = int(vp.value[0].value)
            if prov_id in provinces:
                vps.append({
                    "province": prov_id,
                    "value": int(vp.value[1].value),
                    #"buildings": [bld.id for bld in st.get_bld_list() if int(bld.id) == prov_id]
                    "name": locs.get(f"VICTORY_POINTS_{prov_id}")
                })
    return vps

def set_victory_points(vps):
    locs = LocFile(VPS_LOC_PATH)
    states = get_all_states()
    changed_states = set()

    for vp_data in vps:
        prov_id = vp_data["province"]
        value = vp_data["value"]
        name = vp_data["name"]
        loc_key = f"VICTORY_POINTS_{prov_id}"

        for st in states:

            if prov_id in st.province_list: # found correct state
                history = st.pObj.Get("history") if st.pObj.Has("history") else None

                # Find existing VP entry for this province (if any)
                existing_vp = None
                for vp in st.get_vp_list():
                    if int(vp.value[0].value) == prov_id:
                        existing_vp = vp
                        break

                if value <= 0:
                    # Remove existing VP if it exists
                    if history is not None and existing_vp is not None:
                        history.value.remove(existing_vp)
                        changed_states.add(st)

                    # Optional: clear localisation entry if it exists
                    if locs.get(loc_key) is not None:
                        # We can't truly delete lines via LocFile, but we can blank the name
                        #locs.set(loc_key, "")
                        locs.remove(loc_key)
                        
                else:
                    # Add or update VP entry
                    if history is not None:
                        if existing_vp is not None:
                            # Update VP value
                            existing_vp.value[1].value = str(value)
                        else:
                            # Insert new VP history entry
                            history.Insert(f"victory_points = {{ {prov_id} {value} }}")
                        changed_states.add(st)

                    # Update localisation (name may be empty to keep or blank out)
                    if name is not None and name != "":
                        if locs.get(loc_key) is not None:
                            locs.set(loc_key, name)
                        else:
                            locs.add(loc_key, name)

                # Done with this province; no need to check other states
                break
    # Save all modified state files
    for st in changed_states:
        st.save_to_file()

    locs.save(VPS_LOC_PATH)