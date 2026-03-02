

import json
import copy
import random


request_template = {
    "key": "image_request_NUM",
    "request": {
        "contents": [{
            "parts": [
                {"text": "PROMPT"},
                # {
                #     "file_data": {
                #         "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/j0kl7qzfax5x", 
                #         "mime_type": "image/png"
                #     }
                # },
                # {
                #     "file_data": {
                #         "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/u6sf98te3f9r", 
                #         "mime_type": "image/png"
                #     }
                # },
                # {
                #     "file_data": {
                #         "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/edi9b55ah14s", 
                #         "mime_type": "image/png"
                #     }
                # }
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/7ilqxjs69z2f", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/fnxfos8tvdec", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/ypth16rmwf4b", 
                        "mime_type": "image/png"
                    }
                },
                # {
                #     "file_data": {
                #         "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/q8qtp0mm1ra9", 
                #         "mime_type": "image/png"
                #     }
                # },
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

# FOCUS ICONS
# prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. 
# I've attached some example images as a style guide, which would correspond to the following prompts:
# "A trio of medieval soldiers with leather armor and swords",
# "A red medieval flag waving in the wind",
# "Faramir and Eowyn from LOTR holding hands while getting wed".

# **Artistic Style (Reference Examples):**
# Follow the hand-illustrated, realistic style of these examples. Avoid flat colors, black outlines, and cartoon aesthetics.
# $RANDOM$

# **Readability & Scale:**
# The final icon will be displayed at a small size (200x200). To ensure clarity at this scale:
# - Focus on a **strong, recognizable silhouette**.
# - Don't use black outlines, use an oil/acryl painting aesthetic.
# - Prioritize the "feel" of the texture over microscopic details that would disappear when shrunk.
# - Avoid excessive detail that would clutter the small icon.
# - Use a realistic style that matches the medieval Lord of the Rings movie aesthetic.

# **Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

# **Subject to generate:** PROMPT
# """


# LAURELS
# prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. You will be generating images of laurels, decorations and frames for various icons and UI components.
# I've attached some example images of such elements as a style guide.

# The final icon will be displayed at a small size. To ensure clarity at this scale: Focus on a **strong, recognizable silhouette**.

# **Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

# **Prompt to generate:** PROMPT
# """


# GENERIC DECORATIVE
# prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. You will be generating generic decorative assets for various icons and UI components, such as ribbons, dividers, decorations etc.
# I've attached some example images of such elements as a style guide.

# The final icon will be displayed at a small size. To ensure clarity at this scale: Focus on a **strong, recognizable silhouette**.

# **Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

# **Prompt to generate:** PROMPT
# """


# # GENERIC ASSETS
prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. You will be generating generic assets for various icons and UI components.
I've attached some example images of such elements as a style guide.

The final icon will be displayed at a small size. To ensure clarity at this scale: Focus on a **strong, recognizable silhouette**.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Prompt to generate:** PROMPT
"""


prompt_list = [
"A small, hidden forge in a cave, crafting black iron nails.",
"A silhouette of an Orc supervisor overlooking a shallow pit mine.",
"An Orc messenger stealthily handing a sealed scroll to a human in the shadows.",
"A stack of new, crudely made wooden shields bearing a faint, painted eye.",
"A single Orc worker clumsily hammering on a section of a siege tower.",
"A map of a single border region with small, red pinpricks.",
"A pair of Orcs attempting to train a wild warg with meat.",
"A clandestine gathering of men in a back alley, receiving gold.",
"A small pile of collected wood near a freshly dug foundation.",
"A single Orc scout observing a human village from a distant ridge.",
"A row of five identical siege ladders being constructed simultaneously.",
"An Orc overseer lashing a human slave in a larger quarry.",
"A group of Orcs marching with purpose under a larger, clearly visible banner of the Eye.",
"A stack of iron ore and charcoal at the base of a roaring furnace.",
"A black-feathered crebain carrying a small, coded message.",
"A section of the Black Gate being reinforced with new iron plates.",
"A supply caravan of massive wagons moving along a dusty road.",
"An Orc Shaman performing a ritual over a pile of crude weapons.",
"A group of Haradrim warriors, identifiable by their colorful clothing, setting up a small camp.",
"A large, circular pit containing dozens of actively training wargs.",
"A massive, intricate wooden frame of a siege tower under construction.",
"A powerful Orc captain with scars and a prominent helmet, reviewing a large battle plan.",
"A great beast of burden, an Oliphaunt, partially armored and pulling a heavy load.",
"Dozens of furnaces belching black smoke into the air.",
"A great forge crafting a single, large iron battering ram head.",
"A long line of Orcs in uniform, marching past a reviewing stand.",
"A prominent, well-guarded black stone tower, fully built, overlooking a region.",
"An emissary of Sauron, cloaked, speaking openly to a group of Easterlings.",
"A large, clear map showing multiple arrows pointing toward Free Peoples' borders.",
"A collection of varied siege engines—catapults, ballistae, and towers—assembled in a field.",
"A huge battering ram, 'Grond', its wolf-head front clearly defined, being pushed.",
"A Nazgûl on a fell beast, its wings wide, high above a marching army.",
"A deep chasm filled with industrial machinery and thousands of working slaves.",
"The ground cracking and molten lava flowing out near a fortress foundation.",
"A large, well-stocked armory, row upon row of spears, shields, and armor.",
"A grand, imposing black stone palace with many banners of the Eye flying.",
"A great pit containing a captive troll being prodded by multiple Orcs.",
"A vast assembly of ships with black sails, a black fleet, at a crude dock.",
"A large-scale production line of a single type of weapon, like black bows.",
"A group of Orcs and Men in black uniform, training together with a common purpose.",
"A tidal wave of Orcs, Trolls, and Easterlings rushing forward.",
"A group of Nazgûl, all nine, standing in a circle, their cloaks billowing.",
"A great ash cloud from Mount Doom totally obscuring the sun over a battlefield.",
"The Flaming Eye of Sauron, massive and overwhelming, gazing directly from Barad-dûr.",
"A single Orc hand, covered in blood, holding a broken white tree crown.",
"A pile of thousands of Free Peoples' helmets, a mountain of defeat.",
"A map of Middle-earth completely covered by red shade.",
"A grand victory arch in Mordor, adorned with the banners of defeated nations.",
"A vast, empty plain with only a few standing ruins of a human city.",
"The One Ring on Sauron's armored finger, glowing with power over a defeated army.",
"A Hobbit tending to a garden, oblivious to a dark, distant cloud.",
"A Palantir showing only a faint, flickering red light.",
"A single, unlit beacon on a grassy hill.",
"A group of Gondorian soldiers casually drinking in a tavern.",
"A human child playing with a wooden sword, pretending to fight Orcs.",
"A farmer discovering a crudely made Orc arrow in his field.",
"A small group of refugees with few belongings, walking along a road.",
"A few nervous-looking guards at a border post.",
"A single, tattered banner of Gondor, waving in the wind.",
"A map of a region with one small Orc raid marked in red.",
"A group of soldiers actively reinforcing a city wall with stone and wood.",
"Multiple beacons on different hills, all actively on fire.",
"Refugees crowding into a fortified city gate.",
"A blacksmith's forge, working to repair existing weapons.",
"A line of soldiers in formation, swords and spears held ready.",
"A group of leaders from different regions gathered around a war table.",
"A prominent, well-manned watchtower on a border, looking out.",
"A stack of new, clearly made weapons like long spears.",
"A group of horsemen, Riders of Rohan, preparing to set out on patrol.",
"A map of multiple regions with several overlapping battle lines.",
"A large, fortified city with its gates closed, surrounded by a moat.",
"Massive trebuchets and catapults positioned on city walls.",
"Rows of soldiers in heavy armor, shields interlocked in a 'testudo' formation.",
"A group of civilians, including women and children, receiving basic weapon training.",
"A prominent leader, perhaps a king, addressing an assembled army.",
"Multiple large banners of different Free Peoples flying from a single high tower.",
"Wounded soldiers being tended to in a crowded field hospital.",
"A large-scale production line of uniform armor and shields.",
"A vast assembly of soldiers, horses, and wagons in a massive encampment.",
"A map of all Middle-earth with multiple large red 'X's marking active fronts.",
"A soldier making a last stand against multiple Orcs, his sword broken.",
"A great, imposing white stone fortress with its walls crumbling under attack.",
"The Flaming Eye of Sauron gazing over a burning human city.",
"A group of civilians and soldiers huddling in terror in a dark cellar.",
"A broken banner of the White Tree, trampled in the mud.",
"A group of women and children crying over dead soldiers.",
"A final defense line of old men and young boys holding spears.",
"A map of Middle-earth, almost entirely shaded in red, with only one small pocket of white.",
"A group of soldiers making a final, desperate charge at the Black Gate.",
"A single, beautiful white tree, with all its leaves gone, under a dark cloud.",
"An Orc worker clumsily hammering on a section of a siege tower.",
"A stack of new, crudely made wooden shields bearing a faint, painted eye.",
"An Orc supervisor overlooking a shallow pit mine.",
"A silent Orc spy peering out from between thick bushes.",
"A map of a single border region with small, red pinpricks.",
"A small pile of collected wood near a freshly dug foundation.",
"A few Orc scouts observing a human village from a distant ridge.",
"A small, hidden forge in a cave, crafting black iron nails.",
"A row of five identical siege ladders being constructed simultaneously.",
"An Orc messenger stealthily handing a sealed scroll to a human in the shadows.",
"A pair of Orcs attempting to train a wild warg with meat."
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