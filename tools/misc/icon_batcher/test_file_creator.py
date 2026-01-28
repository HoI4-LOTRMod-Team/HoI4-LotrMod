

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

#random_insert = """This icon is for the Spiders of Mirkwood, so stick to a red and black, aggressive theme."""
random_insert = ""

random_chance = 0.5

prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. 
I've attached some example images as a style guide, which would correspond to the following prompts:
"A trio of medieval soldiers with leather armor and swords",
"A red medieval flag waving in the wind",
"Faramir and Eowyn from LOTR holding hands while getting wed".

**Artistic Style (Reference Examples):**
Follow the hand-illustrated, realistic style of these examples. Avoid flat colors, black outlines, and cartoon aesthetics.
$RANDOM$

**Readability & Scale:**
The final icon will be displayed at a small size (200x200). To ensure clarity at this scale:
- Focus on a **strong, recognizable silhouette**.
- Don't use black outlines, use an oil/acryl painting aesthetic.
- Prioritize the "feel" of the texture over microscopic details that would disappear when shrunk.
- Avoid excessive detail that would clutter the small icon.
- Use a realistic style that matches the medieval Lord of the Rings movie aesthetic.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Subject to generate:** PROMPT
"""


prompt_list = [
    "A map of northern river valleys with a railway track sketch drawn over it",
    "A heavy iron crown resting on top of a brown bear fur pelt",
    "A jagged, dark mountain peak casting a long ominous shadow over a green valley",
    "A broken olive branch lying next to a sharpened iron sword",
    "Three distinct hands clasping together over a rustic wooden table in a pact",
    "A large bear paw print stamped onto a royal parchment decree",
    "A silhouette of a new leader stepping out from behind a curtain, mysterious atmosphere",
    "A messenger carrying a scroll walking on a road towards a distant triangular mountain",
    "An open letter with a geometric dwarven rune seal requesting aid",
    "Multiple banners of different northern clans raised together against a snowy backdrop",
    "A heavy dwarven pickaxe striking a rock with sparks flying",
    "A large wooden shield barring a door, symbolizing isolationism",
    "A pair of glowing bear eyes peering out from dark dense forest foliage",
    "A single large banner waving in the wind with a judge's gavel resting below it",
    "A gathering of tribal chieftains sitting around a central campfire",
    "A mailed fist punching forward aggressively, leading a charge",
    "A war horn being blown with visible sound waves, rallying troops",
    "A blueprint sketch of a heavy wooden chariot with spiked wheels",
    "A stack of golden honeycakes on a plate with a bee flying nearby",
    "A bloody dagger stabbed into the seat of a wooden throne",
    "A figure standing on a hill looking towards the west, hand shading their eyes",
    "A sword plunged into a map of the Anduin river valley",
    "A rider on horseback galloping across a grassy plain carrying a message scroll",
    "A brown wizard's staff and a bird carrying a letter in its beak",
    "A brass scale balancing gold coins on one side and a parchment scroll on the other",
    "Three distinct shields arranged in a tight circle, touching edges",
    "A hand offering a formal invitation letter with a floral wax seal",
    "A hand offering a wooden staff or token to a figure in the forest",
    "A sack of grain being exchanged for a steel ingot",
    "Workers constructing a stone defensive wall with wooden scaffolding",
    "A dark, iron gauntlet shaking a human hand, shadowy atmosphere",
    "A human soldier standing shoulder to shoulder with a dwarven soldier",
    "A human smith and a dwarf smith working together on the same anvil",
    "A watchtower covered in snow overlooking a northern mountain pass",
    "Soldiers marching forward through a heavy blizzard",
    "A grand stone building with tall windows and shelves of books visible inside",
    "An open book on a desk with a magnifying glass and a candle",
    "A wooden gavel split in half down the middle",
    "A mouth covered by a piece of cloth, symbolizing silencing opposition",
    "A hand crumbling up an old piece of parchment treaty",
    "A honeycomb dripping red blood instead of honey",
    "A hunter skinning a deer in a self-sufficient forest camp",
    "A lone cabin in the woods with smoke rising from the chimney",
    "A heavy, impregnable stone fortress sitting atop a grey hill",
    "Five old men in robes sitting in a semi-circle debating",
    "A bust or statue of a stern man carved from grey stone",
    "A muscular warrior holding a climbing axe on a high rocky ledge",
    "A prison cell door being locked with a heavy key",
    "A thatched-roof cottage engulfed in flames",
    "A large boot stepping on a flag with a flower emblem",
    "A bird cage with a captured hawk inside",
    "Two armies clashing in a river valley",
    "Archers firing arrows into a dense forest",
    "Bags of gold coins being handed to a green orcish hand as tribute",
    "A caravan of wagons moving through a snowy tundra",
    "A stone statue of a dwarf being defaced or toppled",
    "Ladders being raised against a dark, snowy fortress wall",
    "A finger pointing aggressively at a specific territory on a map",
    "A pile of scrolls, books, and scientific instruments on a desk",
    "A sun rising over the Anduin valley, illuminating a golden banner",
    "An owl perched on a stack of leather-bound books",
    "A close up of a blacksmith's hammer striking red-hot metal",
    "A busy carpentry workshop with saws and tools hanging on the wall",
    "A wagon filled with books traveling along a dirt road",
    "A soldier rappelling down a steep cliff face with ropes"
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