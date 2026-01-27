

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/j0kl7qzfax5x", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/u6sf98te3f9r", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/edi9b55ah14s", 
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

random_insert = """This icon is for Goblin Town, so stick to brownish colors and subterranean themes."""

random_chance = 0.5

prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. 
I've attached some example images as a style guide, which would correspond to the following prompts:
"A trio of medieval soldiers with leather armor and swords",
"A red medieval flag waving in the wind",
"Faramir and Eowyn from LOTR holding hands while getting wed".

**Artistic Style (Reference Examples):**
Follow the realistic style of these examples. Avoid flat colors, black outlines, and cartoon aesthetics.
$RANDOM$

**Readability & Scale:**
The final icon will be displayed at a small size (200x200). To ensure clarity at this scale:
- Focus on a **strong, recognizable silhouette**.
- Use **bold primary forms** to define the shape.
- Prioritize the "feel" of the texture over microscopic details that would disappear when shrunk.
- Avoid excessive detail that would clutter the small icon.
- Use a realistic style that matches the medieval Lord of the Rings movie aesthetic.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Subject to generate:** PROMPT
"""


prompt_list = [
    "A goblin holding a torch and a sack of loot in a burning village",
    "A goblin hand shaking a human hand over a pile of gold coins",
    "A pile of swords and shields with price tags attached",
    "A wooden toll gate on a snowy mountain pass with a goblin guard",
    "Goblins mining with pickaxes in a dark crystal cavern",
    "Rickety wooden bridges connecting two cliff faces over a chasm",
    "A large heap of gold coins, gems, and goblets in a cave",
    "A heavy iron chest with a crude goblin crown resting on top",
    "Two goblin politicians arguing heatedly in a dimly lit tunnel",
    "A goblin wearing spectacles examining a blueprint by candlelight",
    "A goblin blacksmith sharpening a serrated scimitar on a grindstone",
    "A large whip cracking down onto a stone floor",
    "A shadowed figure holding a dagger behind their back, finger to lips",
    "A barricade made of scrap metal, wood, and stones blocking a tunnel",
    "A narrow mountain pass filled with spikes and traps",
    "Goblins stacking heavy grey stones to build a defensive wall",
    "A goblin blowing a crude war horn, summoning others from holes",
    "Wooden barrels and sacks of grain stacked high in a pantry",
    "A disorganized pile of rusty metal scrap and large rocks",
    "A map of a cave system with structural weak points marked in red",
    "A red alarm bell or gong being struck by a panic-stricken goblin",
    "A lone goblin warrior standing defiant on a pile of rubble",
    "Multiple war horns blowing in unison",
    "Wooden mine supports snapping and rocks falling to block a tunnel",
    "A mining pickaxe transforming into a sword",
    "Heavy iron reinforced doors shut tight with multiple wooden bars",
    "Glowing goblin eyes peering out from dark crevices in a cave wall",
    "An empty wooden bowl and a skeleton in a cage",
    "A dagger striking out from a cloud of black smoke",
    "A mob of angry goblins armed with farm tools and clubs",
    "A shield wall deflecting a volley of arrows",
    "A fortified castle built inside a massive underground cavern",
    "A line of goblins in chains carrying heavy rocks",
    "Goblins widening a narrow tunnel with hammers and chisels",
    "A mountain side heavily excavated exposing bare rock",
    "A whip and an hourglass, symbolizing forced labor",
    "A bucket of cold water being poured on a sleeping goblin",
    "A weapon cobbled together from bone, scrap metal, and leather",
    "Raw ore being smelted and hammered into a blade",
    "A collection of nasty, serrated goblin blades",
    "Goblins repairing a dangerous rope bridge with fresh planks",
    "A dead deer being dragged into a cave entrance",
    "A heavy hammer striking a chain on an anvil",
    "A massive stone forge glowing with intense orange fire",
    "A feast of roasted meat on a rough wooden table",
    "Minecarts filled with supplies moving along rusty rails",
    "A plate containing only a fish bone and a crust of bread",
    "Debris and rubble being hauled out of a deep vertical shaft",
    "Goblins carrying lumber and tools for building",
    "A large mound of wood burning into charcoal",
    "A cellar completely filled with crates and barrels",
    "An empty coin purse and a belt tightened to the last hole",
    "A goblin mother surrounded by many small goblin children",
    "A cluttered workshop with tools scattered on a workbench",
    "Many small arrows merging into one large arrow pointing up",
    "A snowy mountain path being cleared of rocks and debris",
    "A goblin whispering lies to two different human figures",
    "A marketplace stall set up at the mouth of a cave",
    "A wax-sealed letter being handed to a hillman warrior",
    "A goblin toll collector weighing a heavy bag of gold",
    "A messenger goblin running across a marshy field",
    "A goblin fist slamming down on a map of the mountains",
    "Merchant caravans travelling along a mountain road",
    "Hordes of goblins pouring out of a mountain gate",
    "A burning house with a goblin running away with loot",
    "Goblins sneaking through the elegant architecture of Rivendell at night",
    "A white flag raised over a chest of gold",
    "A figure bound in ropes being led away by goblins",
    "Shadowy figures trading goods in a dark alley",
    "A welcoming sign above a dark cave entrance",
    "Crates of fine wine and silk stored in a dirty cave",
    "Goblins trekking through a dark forest filled with spiderwebs",
    "A signpost pointing to Bree with a goblin lurking in the bushes",
    "A merchant wagon with a broken wheel and spilled goods",
    "A bustling underground bazaar lit by torches",
    "A rack of weapons with price tags in gold coins",
    "A mercenary contract nailed to a wooden board",
    "Supply wagons loaded with weapons leaving a fortress",
    "A goblin king sitting on a throne made of stolen loot",
    "A unit of goblin mercenaries marching off to war",
    "A terrifying goblin face looming over a pile of treasure",
    "A large hand scooping a significant portion of coins from a pile",
    "A ledger book and an abacus with growing numbers",
    "A gavel crushing a small goblin figure",
    "A map of Middle-earth with Goblin Town highlighted in red",
    "A goblin sitting on a fence watching battles on both sides",
    "A goblin bowing before the flaming Eye of Sauron",
    "A crazy-looking goblin with swirling eyes and a drooling mouth",
    "Goblins frantically writing on scrolls in a library",
    "A massive explosion blasting apart a rock wall",
    "A laboratory flask and a stack of books",
    "Goblins marching in formation performing drills",
    "A spotlight shining on one goblin among a group",
    "Goblins ambushing enemies in a tight tunnel",
    "A bag of gold being exchanged for a scroll of knowledge",
    "A waterfall of gold coins flowing into a chest",
    "A peace treaty signed with a bloody handprint",
    "A goblin blowing a raspberry and making rude gestures",
    "Dark, jagged crates of supplies arriving from the east",
    "Ragged goblins climbing up a mountain to join the army",
    "A sword stabbed into a map of the Rhudaur region",
    "Flames engulfing a map of the Gladden Fields",
    "A crown resting on the peak of a high mountain"
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