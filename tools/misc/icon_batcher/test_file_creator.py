

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/quwydwjmpb04", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/2jrh2spqf0s6", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/99588adfghzv", 
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

random_insert = """This icon is for Lothlorien, so stick to silvery, ethereal tones and light blue and/or green colors."""

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
"A map of Middle-earth with a red shadow spreading from the east towards the Golden Wood",
"A golden crown split in half, one side silver and one side gold, representing a divided rule",
"Elven ships sailing towards a setting sun on the horizon",
"An elven hand placing a wax seal on a parchment decree",
"A ballot box made of white wood with intricate elven carvings",
"Golden lanterns hanging from Mallorn tree branches during a festival",
"Three elven lords sitting in a circle in council",
"Lady Galadriel raising a hand with the ring Nenya glowing white",
"Lord Celeborn standing sternly with a drawn silver sword",
"An hourglass with golden sand that never runs out",
"A high hedge of thorny vines blocking a path completely",
"A closed golden gate reinforced with crossed spears",
"A silvery mist hiding a white city from view",
"An elven warrior in a cloak blending perfectly into a tree trunk",
"A single white candle burning brightly against a consuming darkness",
"An elven shield chipped and battered but still holding firm",
"A sword half-drawn from a scabbard",
"A radiant shield emitting beams of white light",
"A massive stone fortress tower overlooking a river",
"Lembas bread wrapped in a green mallorn leaf",
"A pocket watch hanging from a tree branch",
"A balance scale made of silver with a feather on one side",
"Elven archers standing on stone battlements of Helm's Deep",
"The White Tree of Gondor with a golden leaf falling near it",
"A dagger stabbing into a map of Mordor",
"Galadriel pouring glowing water from a silver pitcher",
"A hand touching dead soil and a flower blooming instantly",
"A glowing hammer striking an anvil with magical sparks",
"The Star of Fëanor emblem in silver",
"A jeweled tiara set with a shining silmaril-like gem",
"An open book with glowing runes floating above the pages",
"Seven swords raised together in a solemn oath",
"A pristine elven helmet with a high crest",
"A golden necklace with intricate gem settings",
"Three gems representing air, earth, and water",
"A white tower falling amidst flames",
"A white ship sailing into a beam of light",
"An old elf looking wistfully at the western horizon",
"A garden at dusk with glowing flowers and fireflies",
"A small hobbit hand holding a slender elven hand",
"A wooden staff and a green cloak worn by a wanderer",
"A silver harp resting by a stream",
"A deer with antlers made of tree branches",
"A map with new paths drawn in green ink",
"Haldir drawing a bow with a stern expression",
"Two hands holding a glowing sapling",
"A quill writing on a scroll over a map",
"A wooden palisade wall reinforcing a forest border",
"A massive Mallorn tree with golden leaves glowing",
"A city built on platforms high within giant trees",
"A hill covered in white flowers",
"A blueprint of a wooden platform construction",
"Two intertwining trees forming a heart shape",
"An elven boat patrolling a river",
"An elf looking through a spyglass over water",
"Stone blocks reinforcing a riverbank",
"A merchant barge filled with barrels floating down a river",
"Scrolls stored in crystal tubes",
"Shelves of books spiraling up a tree trunk",
"A fortress carved into the side of a mountain",
"Crates and barrels stacked inside a massive tree hollow",
"A magical barrier line drawn on the ground",
"A glowing blue orb of wisdom",
"A rack of curved elven swords",
"Blue flames burning in a forge",
"A sword blade glowing blue in the dark",
"A hooded elf holding dual daggers",
"A white horse with light armor",
"A longbow and a quiver of white-fletched arrows",
"An arrowhead gleaming with silver light",
"Footprints in mud that disappear halfway",
"An elf riding a horse through dense forest",
"An elf in golden armor guarding a pass",
"A spear with a banner of the golden flower",
"Celeborn walking away into the mist with his back turned",
"An elven boot stepping on an orc helmet",
"A sleeping elf opening glowing eyes",
"Galadriel wearing a crown made of sun rays",
"Soldiers in silver armor standing at attention",
"A portrait of Dark Galadriel with a stormy background and glowing aura",
"A white crystal, flawless and shining",
"Elves in fine silk robes looking down haughtily",
"Galadriel and Celeborn clasping hands in unity",
"A silver and gold yin-yang style symbol",
"Two ghostly figures whispering to a living elf",
"A signed treaty with two distinct wax seals",
"A grey cloak and a silver brooch",
"A statue of a tall grey elven king",
"A magical shimmering barrier protecting a forest",
"A cave entrance that looks welcoming and lit by torches",
"A seagull flying towards a coastal tower",
"A silver crown resting on a velvet cushion",
"A symbol mixing a tree and a stone",
"A bard singing with a lute",
"A silhouette of a couple holding hands under the moon",
"A handsome elf holding a Silmaril",
"A flying ship sailing in the night sky",
"A crown of Númenor",
"A portrait of Elrond looking wise",
"The waterfalls of Rivendell",
"A lighthouse beam cutting through fog",
"Three different elven banners tied together",
"Nobles bowing to a common cause",
"Soldiers of different regiments marching together",
"A dove breaking a metal chain",
"An elf and a man shaking hands",
"A hand holding a glowing green vine",
"A vial of glowing water",
"Treebeard's face formed from bark and moss",
"A giant bear and a stag standing together",
"A giant eagle swooping down",
"A fellbeast screeching in the sky",
"A giant spider web with dew drops",
"A path leading between dark trees and light trees",
"A giant spider wearing a crown",
"An elf hand calming a wolf",
"An elf and a dwarf drinking ale together",
"The silhouette of the Lonely Mountain",
"The Doors of Durin glowing in the dark",
"A scroll with a heavy wax seal demanding action from Thranduil",
"The Arkenstone glowing brightly",
"A sword and a plowshare crossed",
"A white horse galloping on green grass",
"A monument stone on a grassy field",
"Mist covering an army of horsemen",
"A herald with the tree of Gondor on his tabard",
"Grey-cloaked rangers walking in the rain",
"A shield wall of mixed races",
"The Lothlórien flag waving alone",
"An elf giving bread to a beggar",
"A tent camp set up under golden trees",
"A sunburst emblem",
"An elf reading a dwarven blueprint",
"Galadriel walking into a white light, fading away",
"Celeborn raising a sword in victory",
"A mosaic made of different colored stones fitting together",
"An orc speaking at a podium",
"Footprints leading into uncharted woods",
"Many hands raising tools in unison",
"Celeborn sitting on a high throne",
"A university building built into the trees",
"A hand reaching for a golden crown",
"An old general's baton broken in half",
"A skull wearing a rusted helmet",
"An elven arrow piercing a dwarven shield",
"A sealed mine entrance",
"A burning human village",
"A clock shattering",
"Elves huddled together under a shield",
"Rivendell under a dark banner",
"Mirkwood gates being forced open",
"The Grey Havens burning",
"Blood spattered on a golden leaf",
"A gavel striking a desk",
"A nobleman's wig or hat thrown on the floor",
"Commoners gathering in a town square",
"Sacks of grain being distributed to the people",
"A ladder reaching upwards",
"A leader working in the fields alongside peasants",
"A map with arrows pointing outward from Lothlórien",
"A river valley with wooden cottages",
"An open hand offering a scroll",
"Troops marching north on a map",
"A basket of fruit and wine",
"Two workers building a bridge",
"The three peaks of Moria",
"A torch illuminating a dark tunnel",
"A gate being unlocked",
"A whip of fire in the darkness",
"A dark ruined fortress on a hill",
"Elves building a fence around a dark forest",
"A gauntlet smashing a table",
"The One Ring glowing with fiery script",
"A chair at a stone council table",
"A beautiful hand snatching the Ring",
"A group of nine elves walking in a line",
"The One Ring resting on a velvet pillow",
"The Fellowship walking over a mountain pass",
"Ancient ruins glowing with magic",
"A silver basin filled with water",
"The mirror basin glowing intensely",
"A dusty tome with a lock",
"A golden quill and inkpot",
"Glowing crystals in a dark room",
"The Ring of Water Nenya sparkling",
"Runes floating around a ring",
"A golden globe representing dominion",
"An eye made of starlight",
"Two rings melting into one",
"A black cloak burning",
"Surgical tools on a table",
"An orc helmet painted with elven colors",
"Chains made of gold",
"A shadow shape whispering into an ear",
"A figure pushing back against a wall of shadow",
"Hands offering the ring to a dark armored figure",
"Lady Galadriel in dark armor standing beside the dark lord Sauron",
"An elf and an orc shaking hands awkwardly",
"An orc in chains holding a weapon",
"An orc wearing elven armor",
"An elven bow broken on the ground",
"An Uruk-hai face",
"A banner with a stylized eye and a tree",
"A round table with regional flags",
"A chest of gold arriving",
"Men working in a mine under elven supervision",
"A village elder holding a staff",
"A map being colored in yellow",
"A sawmill in a forest",
"A farm with golden wheat",
"A mine entrance reinforced with wood",
"Coins being counted on a table",
"Elves and Men dancing together",
"A document with a wax seal granting rights",
"A road sign pointing to Lothlórien"
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