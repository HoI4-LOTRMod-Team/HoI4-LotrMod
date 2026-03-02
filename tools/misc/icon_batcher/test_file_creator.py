

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
                        "mime_type": "image/jpeg" # !!!
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
"A Gondorian guard peering East towards a hazy sky",
"A hooded Ranger marking an 'X' on a weathered map",
"Two Elves speaking in hushed tones over a glowing Palantir",
"A Dwarf reinforcing the iron bands of an outpost door",
"A Hobbit listening intently to a troubling rumor in a tavern",
"A lit beacon fire beginning to smoke atop a mountain",
"The Red Arrow of Gondor being handed to a Rohan rider",
"A lineup of volunteers receiving basic spears and shields",
"Workers reinforcing the lower walls of Minas Tirith",
"An Elf archer nocking an arrow on a wooden wall",
"A hand clenching a fist over the White Tree emblem",
"A blacksmith frantically hammering an unfinished longsword",
"A line of soldiers locking shields into a defensive wall",
"A commander shouting orders over a sea of helmets",
"A defiant standard-bearer raising the banner of Rohan",
"A burning village seen through the eyes of a refugee",
"A broken siege engine being used as a crude barricade",
"A group of civilians huddled around a single, dim candle",
"A bloody sword resting beside a cracked helmet on the ground",
"A line of archers firing a volley with gritted teeth",
"A city gate being smashed by a massive battering ram",
"A king leading a desperate, suicidal cavalry charge",
"A wizard's staff clashing against a dark, shadowy mace",
"A lone soldier surrounded by many dark, shadowed figures",
"A commoner wielding a broken table leg as a weapon",
"The White Tree of Gondor wilting and losing leaves",
"The golden hall of Meduseld shadowed by a dark cloud",
"The entrance to Erebor being sealed by massive stones",
"The borders of Lothlórien protected by shimmering, faint magic",
"The Shire's peaceful rolling hills under a grey, unnatural sky",
"The Horn of Gondor being blown with desperate force",
"The Swan Ships of the Grey Havens preparing for departure",
"The Argonath statues seen from below, shadowed and imposing",
"The bridge of Khazad-dûm crumbling into the abyss",
"The Dead Marshes glowing with faint, eerie lights",
"A scroll with a broken wax seal of the White Hand",
"A quiver of arrows being split evenly among three soldiers",
"A hand sharpening a rusted Orc-slaying axe",
"A lone, hooded Ranger tracking prints in the mud",
"A shield painted with a simple, defiant White Tree",
"A messenger bag dropped on a muddy road",
"A pair of binoculars observing a distant, moving dust cloud",
"A group of figures huddled under cloaks in a stone ruin",
"A sword hilt being tightly wrapped with new leather",
"A crude wooden watchtower looking East",
"A pile of weapons and shields collected from the fallen",
"A field hospital tent illuminated from within at night",
"A hand gripping a blood-stained, ornate dagger",
"A line of soldiers marching in silent, grim determination",
"A horse and rider silhouetted against a setting sun",
"A group of children playing soldiers with wooden swords",
"A mother clutching her child tightly in a cellar",
"An old man trying on his rusted, too-small armor",
"A farmer picking up a pitchfork with a grim look",
"A row of empty helmets lined up on a wall",
"A map of Middle-earth with the East covered in shadow",
"A hand dropping a single tear onto a strategy map",
"A glowing blue sword reflecting in a soldier's eye",
"A lone watchman on a high wall looking over a dark plain",
"A cracked and splintered shield resting against a wall",
"A line of torches marching through a dark mountain pass",
"A fortified bridge over a rushing, dark river",
"A small campfire on a high, exposed ridge",
"A group of refugees huddled together for warmth",
"A stone statue of a king, now chipped and broken",
"A group of soldiers sharing a final, meager meal",
"A shield wall locking together under a shower of arrows",
"A line of archers on a wall, arrows nocked and ready",
"A group of knights with lances leveled, ready to charge",
"A commander pointing dramatically to a weak point in the defense",
"A soldier barricading a door with wooden planks",
"A hand holding a simple, small leather pouch",
"A group of figures around a map illuminated by a lantern",
"A stack of new, long spears leaning against a wall",
"A hand clenching a few simple iron coins",
"A blacksmith forging a heavy iron gate",
"A long line of wagons loaded with supplies",
"A hand gripping a blood-stained axe handle",
"A line of soldiers standing watch on a rain-slicked wall",
"A small, hidden encampment in a dense forest",
"A shield painted with the seven stars of Gondor",
"A hand holding a lit torch in a dark cave",
"A line of watchmen on a high wall, peering into the distance",
"A group of soldiers practicing with swords",
"A commander pointing dramatically over a terrain map",
"A burning watchtower silhouetted against the night sky",
"A field covered in the aftermath of a great battle",
"A hand gripping a broken sword hilt tightly",
"A lone soldier standing before a massive, dark army",
"A group of civilians huddled around a wizard's staff",
"A map of Middle-earth with Gondor and Rohan highlighted",
"A hand sharpening a wicked-looking Elf-made dagger",
"A lone hooded Ranger watching from a high cliff",
"A pair of hands gripping a heavy, ornate warhammer",
"A shield painted with a simple, white horse of Rohan",
"A pile of new shields and spears, ready for war",
"A line of arches on a wall, firing downward",
"A group of knights on horseback, charging forward",
"A commander standing defiantly on a broken wall",
"A commoner picking up a sword from a fallen soldier"
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