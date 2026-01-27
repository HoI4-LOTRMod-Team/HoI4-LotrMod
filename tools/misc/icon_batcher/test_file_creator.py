

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

random_insert = """This icon is for the Elves of Mirkwood, so stick to greenish colors and forest themes."""

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
"Thranduil sitting on a throne of carved wood and roots within a great underground hall, warm torchlight",
"A pristine silver elven crown resting on a velvet cushion, symbolizing ancient heritage",
"An elven hand in a leather gauntlet shaking a rugged human hand, symbolizing alliance",
"A map of Mirkwood with red danger markers pinned to the southern borders",
"Heavy reinforced wooden gates barricading a stone cave entrance, defensive structure",
"Elven smiths working on glowing metal at a forge, sparks flying in a dark cave",
"Silhouettes of elven spearmen holding back giant spider legs in a dark forest",
"Workers clearing vines and moss from an ancient paved stone road in the woods",
"A hooded elf peering through a brass spyglass from a high tree branch",
"Scholars from Gondor and Erebor sitting at a table with elves, reading scrolls",
"A heavy iron dungeon door swinging open, light flooding into a dark cell",
"A long wooden banquet table set with wine and fruits under the forest canopy",
"A wooden flet and watchtower platform built high up in a giant mallorn tree",
"An elf in shadow exchanging a sealed scroll with a hunched orc figure",
"Thranduil wearing a crown of autumn leaves, looking proud, haughty and majestic",
"A shining silver shield blocking a wave of black smoke and darkness",
"Three hands touching a sword hilt together: an Elf, a Man, and a Dwarf",
"A single bright white lantern glowing in a dark, oppressive forest, isolationist",
"A burning ring of fire surrounding a mountain forge",
"Legolas standing with a bow, looking conflicted, shadows across his face",
"A seal of a trade guild stamping a parchment document",
"Large wooden silos filled with grain and harvest goods in the forest",
"Blue glowing books and scrolls floating between elven hands",
"Legolas standing at the Council of Elrond in Rivendell, autumnal setting",
"A goblet of Dorwinion wine raised in a toast against a backdrop of a wooden lake town",
"An elf bowing respectfully to a dwarf lord with a red beard",
"Timber logs floating down a river towards a dark ominous land in the distance",
"A glass jar containing a large spider specimen, scientific study",
"A map of the forest being cut in half by a sharp dagger",
"A dusty scroll unfurled showing a complex genealogical family tree",
"An elven officer with a golden insignia on their shoulder, looking down haughtily",
"Two elves dueling with swords in a training ring",
"Elven warriors in cloaks blending perfectly into the bark of trees, camouflage",
"A necklace of sparkling green emeralds in an open wooden box",
"A dwarf's iron helmet with a red cross painted over it, rejection",
"Thranduil and King Dain Ironfoot standing side by side, ready for battle",
"The green banner of Mirkwood flying next to the white tree banner of Gondor",
"Huge stone doors closing, sealing the elves inside a mountain",
"Lady Galadriel in white robes offering a silver phial of light",
"A giant spider burning with green flames, purging the forest",
"A chest overflowing with white gems reflecting starlight",
"Elven arrows being fletched and piled up in massive quantities",
"Dwarven ambassadors being escorted out of elven gates by guards",
"Elven civilians carrying bundles walking away into the deep woods, evacuation",
"Blacksmith tools and anvils being packed into crates hastily",
"A magnifying glass focused on a spider web",
"The dark fortress of Dol Guldur seen through a spyglass, ominous",
"A stack of ancient books, a quill pen, and a candle",
"A dagger and a sealed letter resting on a wooden desk, espionage",
"The heraldry of Doriath (a single star and moon) being raised on a flag",
"Green paint covering a map of the known world's forests, expansion",
"A golden shield protecting a sapling tree",
"Thranduil bathed in golden light, looking god-like and exalted",
"Three thrones arranged in a circle in a forest glade, Council of Three Realms",
"Chains wrapping around a dark tower, containment",
"Mist covering the borders of the forest, hiding it from view",
"Bellows blowing air into a hot forge fire, industrial",
"An elf meditating stoically while shadows surround them",
"A broken elven sword being used as a dagger in desperation",
"A dwarf teaching an elf how to mine stone, sharing knowledge",
"Elven archers and Human swordsmen training together in a field",
"A split face, half fair elf, half scarred orc, duality",
"An ancient elven statue being toppled over and shattered",
"An elf with black veins and sharp teeth, looking powerful but evil and corrupted",
"Rows of orcs and corrupted elves standing in formation together",
"A massive Olog-hai troll in heavy black armor",
"Thranduil bowing in submission before the flaming Eye of Sauron",
"The Lonely Mountain (Erebor) burning in the distance",
"Tauriel hiding in shadows with a dagger, looking at a map",
"The Ring Vilya (Blue stone) on a finger, glowing with power",
"The Ring Nenya (White stone) on a finger, radiating light",
"Magical mist dissipating to reveal a hidden path",
"A Beorning (large man) shaking hands with a wood elf",
"Radagast the Brown with a bird on his hat holding his staff",
"A water wheel built seamlessly into a flowing river in the forest, nature industry",
"Elegant elven spiral staircases wrapped around massive tree trunks",
"A camouflage cloak blending perfectly with autumn leaves",
"A Giant Eagle of Manwe swooping down with talons extended",
"A rack of curved elven swords gleaming in the moonlight",
"A velvet gloved hand holding a puppet string, soft power",
"Barrels of wine being loaded onto a raft, trade",
"An iron cage hanging from a tree branch",
"A dark forest path illuminated by glowing stones",
"Legolas and Tauriel looking at a map of the forest, planning",
"A pile of gold coins being offered in a hand",
"A pickaxe striking stone with a red arrow pointing down, reduced mining"
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