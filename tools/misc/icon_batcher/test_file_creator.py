

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
    "A rustic wooden village surrounded by encroaching dark shadows and threatening shapes",
    "A tense council meeting in a wooden hall with grim-faced elders arguing",
    "A small wooden shield resting beneath a large, ornate iron shield for protection",
    "A solitary woodman standing defiant with an axe against a stormy sky",
    "A rolled parchment scroll sealed with wax resting on a rough wooden table",
    "Two hands clasping together, one rough and gloved, the other armored",
    "A figure kneeling and offering a wooden bowl in submission",
    "The dark silhouette of Dol Guldur rising above twisted trees with green mist",
    "A golden mallorn leaf glowing softly against a dark forest background",
    "An elegant elven shield decorated with autumn leaves and woodland motifs",
    "A rustic riverside hut on stilts near a marshy riverbank",
    "A peasant raising a pitchfork and a torch in alarm",
    "A crowd of villagers gathering with makeshift weapons like axes and spears",
    "A hooded elven archer in a grey cloak camouflaged among tree trunks",
    "A wooden staff topped with a blue crystal and a bird perched on it",
    "A crude, jagged orcish sword crossed with a black whip",
    "Soldiers sparring with wooden practice swords in a forest clearing",
    "Radagast the Brown with a bird on his hat holding a staff",
    "A peaceful village scene with smoke rising from chimneys and a sturdy fence",
    "A woodman shouting and throwing a stone across a border",
    "A wooden watermill wheel turning in a river stream",
    "An open hand extending an olive branch or a message of peace",
    "Suspicious eyes peering out from the darkness of a dense thicket",
    "Labourers constructing a wooden palisade wall in the forest",
    "A bear trap hidden beneath leaves on a forest path",
    "A blacksmith's anvil with a glowing red iron bar being hammered",
    "A wooden cart overloaded with sacks of grain and timber logs",
    "A warrior tightening the straps of leather armor, preparing for battle",
    "A row of sharpened wooden stakes pointing outwards",
    "A stockpile of newly crafted bows and bundles of arrows",
    "A carpenter's workbench covered in wood shavings and tools",
    "An eye formed by the twisting branches of an ancient tree",
    "New log cabins being built on the edge of a forest clearing",
    "A smoking charcoal mound or kiln in the deep woods",
    "A large pile of cut logs and a lumberjack's axe resting on a stump",
    "A reinforced wooden longhouse serving as a town hall",
    "A group of ragged refugees carrying bundles walking through the woods",
    "A workshop hidden inside a cave entrance covered by vines",
    "A clenched fist holding a torch rising from the forest floor",
    "A massive continuous wall of logs stretching across the landscape",
    "A farming scythe being heated and hammered into a weapon",
    "A lone battered warrior making a last stand against shadowy figures",
    "A leather coin purse being squeezed by a hand",
    "A wooden gavel striking a sound block on a council table",
    "A giant spider web with a bundle of trade goods caught in it",
    "A hand gently touching the mossy bark of an old tree",
    "An open field journal with a sketch of a strange woodland beast",
    "Large Rhosgobel rabbits pulling a rustic wooden sled",
    "A hand placing a wooden claim marker on a map of the river valley"
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