

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/yj587cqflt5u", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/fhibmqz0kevn", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/255w4njbla8q", 
                        "mime_type": "image/png"
                    }
                }
                # {
                #     "file_data": {
                #         "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/7ilqxjs69z2f", 
                #         "mime_type": "image/jpeg" # !!!
                #     }
                # },
                # {
                #     "file_data": {
                #         "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/fnxfos8tvdec", 
                #         "mime_type": "image/png"
                #     }
                # },
                # {
                #     "file_data": {
                #         "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/ypth16rmwf4b", 
                #         "mime_type": "image/png"
                #     }
                # },
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
# prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. You will be generating generic assets for various icons and UI components.
# I've attached some example images of such elements as a style guide.

# The final icon will be displayed at a small size. To ensure clarity at this scale: Focus on a **strong, recognizable silhouette**.

# **Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

# **Prompt to generate:** PROMPT
# """


prompt_list = [
"A goblin hiding behind a raised shield",
"A pile of metal scrap and stone",
"A goblin soldier with improvised equipment saluting",
"A goblin soldier with shield and spear holding off a charging human soldier",
"A goblin mustering a wooden support strut with curiosity, thinking",
"A goblin inspecting a wooden support strut with malicious intent",
"A man soldier entering a tunnel, oblivious to the goblins lying in wait to ambush him",
"A goblin merchant offering a rusty sword to a human",
"A white dove of peace on a pile of golden coins",
"A goblin inviting a human soldier to enter a sketchy mountain passage",
"A goblin carrying a crate through a tunnel",
"A goblin scribe",
"A set of books and alchemical flask together with a pouch of coins, to symbolize purchasing knowledge",
"The foundations of future dark construct",
"A freshly born/created orc, wet and slimy, looking at his own arms",
"An orc spying on some Rohirrim riders",
"Traditional crafting techniques from the vales of the Anduin",
"Something symbolizing seasonal (winter/summer) labor cycles",
"Azog the defiler, the white orc",
"Something symbolizing self-sufficiency",
"Something symbolizing the integration of a region",
"Something symbolizing the integration of an administration",
"An Easterling warrior holding up a shield to ward off the Eye of Sauron",
"A fortified wall to ward off the Eye of Sauron",
"A chariot without horse or rider, in storage",
"A smug, arrogant looking elven aristocrat",
"Something symbolizing isolationism",
"A group of soldiers driving off a troll with spears",
"A soldier driving off a troll with a spear",
"A goblin hiding behind a raised shield",
"A pile of metal scrap and stone",
"A goblin soldier with improvised equipment saluting",
"A goblin soldier with shield and spear holding off a charging human soldier",
"A goblin mustering a wooden support strut with curiosity, thinking",
"A goblin inspecting a wooden support strut with malicious intent",
"A man soldier entering a tunnel, oblivious to the goblins lying in wait to ambush him",
"A goblin merchant offering a rusty sword to a human",
"A white dove of peace on a pile of golden coins",
"A goblin inviting a human soldier to enter a sketchy mountain passage",
"A goblin carrying a crate through a tunnel",
"A goblin scribe",
"A set of books and alchemical flask together with a pouch of coins, to symbolize purchasing knowledge",
"The foundations of future dark construct",
"A freshly born/created orc, wet and slimy, looking at his own arms",
"An orc spying on some Rohirrim riders",
"Traditional crafting techniques from the vales of the Anduin",
"Something symbolizing seasonal (winter/summer) labor cycles",
"Azog the defiler, the white orc",
"Something symbolizing self-sufficiency",
"Something symbolizing the integration of a region",
"Something symbolizing the integration of an administration",
"An Easterling warrior holding up a shield to ward off the Eye of Sauron",
"A fortified wall to ward off the Eye of Sauron",
"A chariot without horse or rider, in storage",
"A smug, arrogant looking elven aristocrat",
"Something symbolizing isolationism",
"A group of soldiers driving off a troll with spears",
"A soldier driving off a troll with a spear",
"A goblin hiding behind a raised shield",
"A pile of metal scrap and stone",
"A goblin soldier with improvised equipment saluting",
"A goblin soldier with shield and spear holding off a charging human soldier",
"A goblin mustering a wooden support strut with curiosity, thinking",
"A goblin inspecting a wooden support strut with malicious intent",
"A man soldier entering a tunnel, oblivious to the goblins lying in wait to ambush him",
"A goblin merchant offering a rusty sword to a human",
"A white dove of peace on a pile of golden coins",
"A goblin inviting a human soldier to enter a sketchy mountain passage",
"A goblin carrying a crate through a tunnel",
"A goblin scribe",
"A set of books and alchemical flask together with a pouch of coins, to symbolize purchasing knowledge",
"The foundations of future dark construct",
"A freshly born/created orc, wet and slimy, looking at his own arms",
"An orc spying on some Rohirrim riders",
"Traditional crafting techniques from the vales of the Anduin",
"Something symbolizing seasonal (winter/summer) labor cycles",
"Azog the defiler, the white orc",
"Something symbolizing self-sufficiency",
"Something symbolizing the integration of a region",
"Something symbolizing the integration of an administration",
"An Easterling warrior holding up a shield to ward off the Eye of Sauron",
"A fortified wall to ward off the Eye of Sauron",
"A chariot without horse or rider, in storage",
"A smug, arrogant looking elven aristocrat",
"Something symbolizing isolationism",
"A group of soldiers driving off a troll with spears",
"A soldier driving off a troll with a spear",
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