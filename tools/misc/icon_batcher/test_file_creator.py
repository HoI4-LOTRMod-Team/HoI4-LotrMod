

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
"A large solitary stone rock formation rising from a river valley, view from below looking up",
"A giant eagle landing on a gloved hand, majestic feathers",
"A giant eagle eye close up with a reflection of a mountain range in the pupil",
"A pile of sheep carcasses and gold offerings laid out on a high mountain ledge",
"A jagged mountain peak with a dark ominous cave entrance at the base",
"A torch illuminating a dark tunnel filled with goblin weaponry and debris",
"A stone watchtower built into the side of a snowy mountain pass",
"A human hand shaking a clawed goblin hand, shadows obscuring the faces",
"A burning primitive village on a hill with smoke rising",
"A hidden path winding through steep rocky cliffs, illuminated by a single ray of sunlight",
"Silhouette of a giant eagle flying over a mountain range against a sunset",
"A bearded chieftain sitting on a wooden throne holding a spear, authoritarian style",
"A map of a river valley spread on a table with a dagger stuck into it",
"A blacksmith hammer striking an anvil, sparks flying, with a loaf of bread pushed to the side",
"A gauntleted fist clenching a wooden staff, symbolizing strength over weakness",
"A spear planted in the ground marking a boundary line",
"Three tribal lords standing in a field of iris flowers, conferring together",
"A warrior charging forward with a shield raised, ignoring a warning sign",
"A wooden bridge under construction crossing a wide river, western orientation",
"A paved road winding through green fields near a river bank",
"A large spider web in a dark forest with a map caught in the threads",
"An ancient stone carving depicting a horse and rider",
"A wooden palisade fence facing a dark dense forest",
"A cow tethered to a post near a dark forest edge as an offering",
"A torch setting fire to thick white spider webs",
"A sword cutting through a thick spider web",
"A spool of strong, shimmering white silk thread",
"Two light cavalry riders galloping through a marshy field, wearing leather armor",
"Hooves of galloping horses kicking up dust, low angle view",
"A tactical diagram drawn on parchment showing hit-and-run cavalry maneuvers",
"A mare and foal standing in a fenced wooden paddock",
"Hands of different races (men, elves, dwarves) joined together in a circle",
"A traveler walking down a straight path, looking neither left nor right",
"Two drinking horns raised in a toast against a wooden table",
"A messenger holding a sealed scroll standing before a banner with a white horse",
"A column of riders departing towards a green horizon",
"A round wooden table with several empty chairs waiting to be filled",
"A rustic wooden cottage surrounded by birds and woodland animals",
"A large bear paw print in the mud next to a human footprint",
"A hooded figure presenting a gift to an elven guard at a forest gate",
"A simple iron circlet crown resting on a rough wooden table",
"A shield being held over a smaller, defenseless figure",
"A scout with a spyglass looking out from a tree branch",
"A sword resting in its scabbard but with a hand on the hilt, ready to draw",
"An hourglass with the sand almost run out, next to a weapon",
"A sapling tree growing out of a pile of bricks",
"Golden wheat fields growing along a river bank",
"Stalls with colorful awnings set up along a river pier",
"A heavy bag of coins resting on a military drum",
"Molten metal being poured into a mold in a dark forge",
"Several small clan banners being tied together into one larger bundle",
"A burning torch crossed with a sack of loot",
"A spear pointed at a bear standing on its hind legs",
"Soldiers marching towards a house in the woods",
"A hand handing over a bag of gold to a goblin hand",
"Peasants armed with pitchforks and rudimentary spears",
"A hidden workshop inside a cave lit by lanterns",
"A large rocky cliff ledge reinforced with wooden platforms for eagles",
"A stack of fine elven bows made of white wood",
"A young noble looking at a crown, with a horse motif in the background",
"A golden crown with river-blue gems placed on a map of the Anduin Vales"
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