

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

random_insert = """This icon is for Rohan."""

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
    "The white horse banner of Rohan flying against a stormy sky",
    "Iron pickaxes and raw ore piles in a mine shaft",
    "A hooded scout looking through a spyglass at snowy mountain peaks",
    "Two armored hands shaking in agreement over a stone monument",
    "An ancient weathered scroll resting on a wooden shield",
    "An open book glowing with golden light in a dark room",
    "A sturdy Rohirric shield with a green background and white sun symbol",
    "A weather vane shaped like a horse turning in the wind",
    "Stacked lumber logs and a woodcutter's axe",
    "A blueprint of a fortress being drawn on a table",
    "A smoking industrial chimney and factory gear",
    "A collection of alchemical flasks and engineering compasses",
    "A wagon wheel travelling on a paved road",
    "Ancient stone standing stones winding up a mountain path",
    "Grima Wormtongue whispering into the ear of an old King Theoden",
    "A bag of gold coins being secretly passed between hands",
    "A military helmet being crushed by a dark gauntlet",
    "An eye peering through leaves at an elven building",
    "A hand grasping towards a golden ring on a map",
    "The White Hand of Saruman painted on a black rock",
    "A poster depicting a terrifying orc face to scare civilians",
    "King Theoden sitting alone on a dark throne looking weary",
    "A broken shield with the royal crest lying in mud",
    "Grima Wormtongue sitting at the head of a council table",
    "Scales of justice balanced with a sword",
    "A hand cutting a tax document with a knife",
    "A wooden palisade wall being constructed",
    "A lit beacon fire on a mountain top",
    "The Hornburg fortress of Helms Deep standing strong",
    "The Golden Hall of Meduseld on a hill",
    "King Theoden holding a sword surrounded by loyal advisors",
    "Gandalf the White standing in a bright light holding his staff",
    "A broom sweeping away black snakes",
    "Grima Wormtongue being thrown down the stairs of Edoras",
    "An executioner's axe resting on a block",
    "The Fellowship of the Ring walking in a line silhouette",
    "Rohirrim riders charging into Uruk-hai",
    "Traitorous banners being torn down",
    "The sun rising over the green plains of Rohan",
    "Eomer raising his sword rallying the troops",
    "A herd of wild horses being rounded up",
    "Riders chasing fleeing orcs",
    "A raven flying with a scroll in its beak",
    "Broken chains lying on the ground",
    "Three hands clasping together in a circle",
    "The Red Arrow of Gondor being presented",
    "King Theoden shouting a war cry on horseback leading a charge",
    "King Theoden and Aragorn standing side by side",
    "Treebeard the Ent standing tall in a forest",
    "A silver elven brooch with a green leaf",
    "Saruman's staff and Theoden's sword crossed",
    "A royal crown lying on a tombstone",
    "A marionette puppet dressed as a king with strings attached",
    "Dark storm clouds gathering over the Golden Hall",
    "Eowyn sitting on the throne looking sad and controlled",
    "Grima Wormtongue placing a hand on Eowyn's shoulder",
    "Black banners replacing the green ones on Edoras",
    "A rider kneeling before Saruman the White",
    "Uruk-hai soldiers patrolling Edoras streets",
    "Robed figures with staffs entering the court",
    "A fist smashing a white hand symbol",
    "The Eye of Sauron gazing at a Rohan banner",
    "Nazgul flying over a Rohan army",
    "A golden crown with horse motifs shining brightly",
    "Five different banners representing the regions of Rohan",
    "Wildmen of Dunland armed with axes joining the ranks",
    "Scaffolding around a stone tower in the hills",
    "Carts of grain being delivered to Orthanc",
    "Golden wheat fields stretching to the horizon",
    "Rohan and Elven goods being exchanged",
    "Miners digging into the earth",
    "Tax collectors taking coins from a chest",
    "The green lands of the Eastfold",
    "Lords gathering around a large table in the Golden Hall",
    "Messengers riding out in different directions",
    "A gavel striking a sound block",
    "Gold bars stacked in a vault",
    "A large pile of gold placed on one city on a map",
    "Large grain silos filled to the brim",
    "Workers paving a stone road",
    "Stalls with colorful awnings in Edoras",
    "A diagram of cavalry formations on paper",
    "An armored warhorse with barding",
    "Thousands of spears reflecting the sun in a charge",
    "White limestone bricks stacked neatly",
    "A traditional wooden windmill",
    "A catapult aimed at a wall",
    "White stone masonry similar to Minas Tirith",
    "A crude wooden siege tower with metal spikes",
    "Scrolls stored in wooden racks",
    "Crucible pouring liquid metal",
    "A pestle and mortar with glowing herbs",
    "The black tower of Orthanc with scaffolding",
    "Wedding rings with Rohan and Dol Amroth symbols",
    "Eowyn and Faramir holding hands",
    "Barrels of wine and grapes"
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