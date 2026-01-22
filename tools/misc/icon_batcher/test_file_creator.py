

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
Follow the painterly, hand-illustrated style of these examples. Use muted, grounded colors, realistic textures (metal, cloth, wood), and soft cinematic lighting. Avoid flat colors, thick black outlines, and the "mobile-game cartoon" look.
$RANDOM$

**Readability & Scale:**
The final icon will be displayed at a small size (200x200). To ensure clarity at this scale:
- Focus on a **strong, recognizable silhouette**.
- Use **bold primary forms** and high-contrast lighting to define the shape.
- Prioritize the "feel" of the texture over microscopic details that would disappear when shrunk.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Subject to generate:** PROMPT
"""


prompt_list = [
"A pile of jagged iron swords and shields",
"Dark ominous clouds spreading over a dense forest canopy",
"An orcish whip cracking in the air",
"A single Uruk-hai warrior standing apart from a formation looking ambitious",
"Orcs marching in strict formation on a muddy field",
"A decorated orcish helmet resting on a command table",
"A map of Middle-earth with dark arrows pointing outwards from Mirkwood",
"A dark gauntleted hand crushing a glowing white star",
"Ancient trees being chopped down and burning in a pile",
"Black corrupting sludge flowing into a clear blue river",
"A broken elven bow lying on the forest floor",
"A massive dark iron anvil with a glowing red hammer",
"Battering rams attacking elegantly carved wooden gates",
"A shadowy figure looming over a river bank scaring peasants",
"Glowing yellow eyes peering out from dark bushes",
"Orcish wolf riders crossing a stone ford in a river",
"A wooden totem pole being split in half by a dark wedge",
"A burning horse banner",
"The Eye of Sauron gazing down upon a black fortress",
"A massive armored troll holding a large boulder",
"A clawed hand casting purple necromantic energy",
"Furnaces glowing red in the dark spewing black smoke",
"Rows of jagged metal weaponry on a rack",
"A Palantir glowing faintly in the dark",
"Tall twisted black spires rising above a tree line",
"A green glowing forge with skeletal remains incorporated into the structure",
"Mineshafts digging deep into a rocky hill",
"Orcs clearing away rubble from an ancient ruin",
"Stone blocks being laid down in mud to form a foundation",
"Chains and manacles attached to a dungeon wall",
"Dark mist tendrils wrapping around tree trunks",
"A dark throne made of twisted roots and iron",
"A black rider handing a scroll to an orc commander",
"A shattered image of the Eye of Sauron",
"A giant spider accepting a tribute of raw meat",
"Scaffolding erected around a ruined tower",
"Iron grate doors closing on a dark cell",
"Ghostly whispers depicted as faint wind spirits in a forest",
"A command tent with organized maps and markers",
"A silhouette of a dark fortress against a twilight sky",
"Orcs fighting other orcs in a dark hallway",
"Blueprints of a twisted machine on parchment",
"Heavy stone walls with spikes surrounding a hill",
"Red arrows pushing into a green map area",
"Spider eggs glowing faintly in a web",
"A dark alchemy table with bubbling vials",
"A wall of shadow blocking golden light beams",
"A giant spider caught in iron chains",
"A tall dark tower fully restored and imposing",
"Orcs hauling large stones up a ramp",
"Refining a magical blueprint with a quill",
"Chimneys pumping out thick black smoke into the sky",
"Crates stacked high in a dark stone vault",
"A pit filled with biomass and green magic",
"A golden ring lying on the ground surrounded by shadows",
"A target reticle over a Mallorn tree",
"A target reticle over a dense dark forest",
"Burning white platforms in high trees",
"Watchtowers on the edge of a forest",
"A spear pointing North on a compass",
"Wolves attacking a wooden border fence",
"Elegant elven hands bound in rusted manacles",
"A sack of gold placed on a tree stump",
"Mountain peaks shrouded in storm clouds",
"A goblin messenger in a tunnel holding a letter",
"A horde of orcs rushing down a hill",
"Two orc generals clashing weapons in agreement",
"A burning supply wagon",
"A road being built through tall grass",
"Warg riders chasing horses on open plains",
"A diagram of a horse's anatomy and weak points",
"The White Hand of Saruman shaking a dark gauntleted hand",
"Tents pitched on the edge of a plain",
"Armored wargs with heavy saddles",
"Uruk-hai and Orcs sparring together",
"A dark shadow cast over a map of the East",
"A dark fortress gate closing",
"An anvil and a compass pointing East",
"A golden Easterling mask next to an orc helmet",
"Railroad tracks winding through hills",
"Burning wheat fields",
"A crumbling stone crown",
"A chaotic fire breaking out in a distant city",
"Hundreds of spears raised in the air",
"Warriors training in a dark cave",
"Spiked barricades surrounding a camp",
"An orc looking at the moon waiting",
"Arrows pointing in every direction from a center point",
"A whip striking a spider web",
"An executioner's block with an axe",
"Orcs marching in from a volcanic landscape",
"A complex siege tower design",
"A tactical map with figurines",
"A jagged iron crown resting on a bed of dead leaves",
"Shields facing towards a red glow",
"A dark purple banner with a fortress symbol",
"Old scrolls and books in a pile",
"A serrated blade glowing with heat",
"A heavy sledgehammer striking metal",
"Molten black metal being poured into a mold",
"Black feathered arrows in a quiver",
"A crane lifting a heavy stone block",
"An arrow tip dripping with green venom",
"Gears and cogs grinding together",
"A snarling warg with a saddle",
"A Fellbeast screeching in the sky",
"A clenched fist smashing onto a map",
"Shadows slowly lengthening across the ground",
"Looted goods and weapons piled up",
"A daring thief stealing a gem",
"A heavy lock on a gate",
"Posters with dark symbols plastered on a wall",
"A boot stomping on a rebellious flag",
"Carts filled with ore leaving a mine",
"Peasants or lesser orcs being handed weapons",
"Pack mules walking in a line",
"A book bound in black leather with the Eye of Sauron on it",
"A forest where the trees look like jagged silhouettes",
"A dark laboratory with an open book",
"Three hands grasping a single sword hilt",
"A banner representing different crafting guilds",
"A magnifying glass over a coded letter",
"Gold coins being exchanged in the shadows",
"Mushrooms and dark plants growing in a cave farm",
"Scrolls stored in honeycomb-like stone shelves",
"A balanced scale made of black iron"
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