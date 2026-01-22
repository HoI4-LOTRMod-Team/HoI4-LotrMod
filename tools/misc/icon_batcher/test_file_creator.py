

import json
import copy
import random


request_template = {
    "key": "image_request_NUM",
    "request": {
        "contents": [{
            "parts": [
                {"text": "PROMPT"},
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/rd3lgpq4xta7", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/xtwln2wql745", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/1pxvtlpmx0t3", 
                        "mime_type": "image/png"
                    }
                }
            ]
        }],
        "generationConfig": {
            "responseModalities": [ "IMAGE" ],
            #"temperature": 1.0,
            #"candidateCount": 2,
            "imageConfig": {
                "aspectRatio": "1:1",
                "imageSize": "1K",
                #"personGeneration": "allow_all"
            }
        }
    }
}

random_insert = """This icon is for the orcs of Dol Guldur, so stick to a somewhat darker, evil-looking theme."""

random_chance = 0.5

prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. 
I've attached some example images as a style guide, which would correspond to the following prompts:
"A trio of medieval soldiers with leather armor and swords",
"A red medieval flag waving in the wind",
"Faramir and Eowyn from LOTR holding hands while getting wed".

**Artistic Style (Reference Examples):**
Follow the realistic and cinematic style of these examples. Avoid flat colors, black outlines, and cartoon aesthetics.
$RANDOM$

**Readability & Scale:**
The final icon will be displayed at a small size (200x200). To ensure clarity at this scale:
- Focus on a **strong, recognizable silhouette**.
- Use **bold primary forms** to define the shape.
- Prioritize the "feel" of the texture over microscopic details that would disappear when shrunk.
- Use a realistic looking style, but avoid excessive detail that would clutter the small icon.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Subject to generate:** PROMPT
"""


prompt_list = [
    # Political / Starting Branch
    "A crude iron anvil with jagged orcish weapons piled upon it",
    "Twisted trees of Mirkwood shrouded in a thick unnatural purple fog",
    "A cruel spiked whip resting on a wooden military table",
    "An orc commander pointing forward aggressively, silhouette style",
    "Rows of jagged spears held upright in a disciplined formation",
    "A crude iron military medal embossed with a skull",
    "A tattered map of Mirkwood with aggressive black arrows drawn on it",
    
    # War with Elves / The West
    "An iron gauntlet crushing a glowing white elven gem",
    "Ancient twisted trees engulfed in roaring flames",
    "A river flowing with sickly green toxic water",
    "A broken elven bow lying on dead autumn leaves",
    "A suit of heavy black plate armor glowing with faint red runes",
    "A crude battering ram slamming into elegant wooden gates",
    "A dark silhouette of a boat with a jagged sail on a misty river",
    "Glowing yellow eyes peering out from dark dense bushes",
    "Orcish boots marching across a shallow river ford",
    "A woodman's axe splitting a log in two",
    
    # War with Rohan
    "A burning banner of a white horse falling to the ground",
    "A snarling warg leaping forward aggressively",
    "A heavy spiked saddle designed for a giant wolf",
    "A dirt road winding through grassy plains",
    
    # Mordor / The Necromancer Branch
    "A shadowy figure raising hands with green magical energy",
    "A massive armored troll carrying a large stone",
    "A black grimoire book emitting purple smoke",
    "A furnace glowing with sinister red light",
    "Black hammers striking red hot metal on an anvil",
    "A single flaming eye gazing through a crystal ball",
    "A tall jagged tower with green lightning crackling at the top",
    
    # The Necromantic Forge & Industry
    "A sinister black iron forge emitting green soul-fire",
    "Shovels digging into black cursed earth near ruins",
    "Broken stone pillars being moved aside by ropes",
    "Black stone blocks being laid in a foundation pattern",
    "Rusty iron shackles and chains hanging from a dungeon wall",
    "A dark iron crown resting on a bed of dead black leaves",
    "A black iron chest opening to reveal glowing red light",
    "Wooden scaffolding erected around a dark stone monolith",
    "Stone ramparts and walls built atop a barren hill",
    "Thick black smoke billowing from industrial chimneys",
    "Stacks of crates and barrels in a dark stone room",
    "Twisted organic matter and bones being shaped on a stone slab",
    
    # Spiders
    "A giant spider descending from a web in a dark canopy",
    "A scroll being handed to a giant spider leg",
    "A giant spider rearing up aggressively to attack",
    "A giant spider held down by heavy iron chains",
    "An arrow tip dipping into a vial of green venom",
    
    # Diplomacy / Subterfuge
    "A shimmering magical mask floating in the air",
    "A wall of shadow blocking rays of golden light",
    "A golden ring lying on the ground surrounded by shadows",
    "A crosshair focused on a golden mallorn tree",
    "A crosshair focused on a dark dense forest",
    "A white tree burning with green magical fire",
    "A lonely wooden watchtower on a forest edge",
    "Orcs with torches moving through the night",
    "Elegant elven hands bound by rough iron shackles",
    "An armored hand offering a sack of grain",
    "Snowy mountain peaks looming in the distance",
    "A dark cave entrance with crude wooden supports",
    "Two different orc banners crossed together in alliance",
    "A burning wagon wheel lying in the mud",
    
    # The East / Rhun
    "A black arrow pointing to the right (East)",
    "A smith's hammer pointing towards the sunrise",
    "A golden Easterling mask",
    "Ox-drawn carts carrying supplies",
    "Fields of golden wheat set on fire",
    "A stone statue of a human king toppling over",
    
    # Late Game / Magic / Research
    "A plume of smoke rising in the distance from an explosion",
    "A muscular orc arm flexing",
    "Silhouettes of soldiers training in the moonlight",
    "A perimeter of wooden spiked barricades",
    "An unlit beacon pile of wood ready to burn",
    "Arrows pointing outwards in four directions from a center point",
    "A heavy wooden yoke placed on a beast of burden",
    "An armored gauntlet stopping a knife strike",
    "Chunks of raw meat hanging on a hook",
    "A siege catapult loaded with a large rock",
    "An ornate black iron helmet with a plume",
    "A jagged iron crown glowing with green light",
    "A shield facing towards the rising sun",
    "A landscape bathed in purple twilight",
    "A pile of scrolls and strange potion bottles",
    "A serrated steel blade close up",
    "A heavy two-handed sledgehammer",
    "Molten black iron being poured into a mold",
    "A quiver full of black-feathered arrows",
    "A trowel laying mortar between black bricks",
    "Large wooden gears and chains of a war machine",
    "An armored orc riding a wolf",
    "The leathery wing of a fellbeast against the sky",
    "A fist slamming down onto a map",
    "Shadows lengthening across a forest floor",
    "A book open next to a pile of looted gold",
    "A hand moving a chess piece aggressively",
    "The southern part of a map highlighted in dark ink",
    "A parchment poster nailed to a tree",
    "An armored boot stepping on a broken shield",
    "A mine cart overflowing with ore",
    "Spears being handed out to a crowd",
    "A pack mule walking along a forest trail",
    "A black iron key opening a heavy tome",
    "Trees with twisted branches resembling claws",
    "A heavy iron door leading to a laboratory",
    "A bundle of black iron rods tied together",
    "Golden coins mixed with craftsman tools",
    "A stack of secret documents stamped with a seal",
    "A hooded figure exchanging a bag of coins",
    "Mushrooms growing on a rotting log",
    "Shelves filled with dusty scrolls and books",
    "A secure vault door made of black iron"
]

requests_list = [

]


i = 1
for prompt in prompt_list:
    p = prompt_template.replace("PROMPT", prompt)
    if random.random() < random_chance:
        p = p.replace("$RANDOM$", random_insert)
    req = copy.deepcopy(request_template)
    req["key"] = req["key"].replace("NUM", str(i))
    req["request"]["contents"][0]["parts"][0]["text"] = req["request"]["contents"][0]["parts"][0]["text"].replace("PROMPT", p)

    requests_list.append(req)

    i += 1



json_file_path = 'batch_image_gen_requests.json'

print(f"\nCreating JSONL file: {json_file_path}")
with open(json_file_path, 'w') as f:
    for req in requests_list:
        f.write(json.dumps(req) + '\n')