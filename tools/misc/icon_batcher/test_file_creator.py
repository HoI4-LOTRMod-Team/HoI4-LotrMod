

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/kcvgkmrmr6ag", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/wjs4n8hyb6nc", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/jfvkjhg9fkax", 
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
"An Easterling soldier from the front wearing boxing gloves, with some bruises/damage from a boxing match, but still ready to strike",
"A hand holding a bloody dagger with a mountain range in the background",
"An Uruk-Hai in full armor making notes on a clipboard, with a Kanban board behind him",
"A rotten/tainted piece of wheat, symbolizing a bad harvest",
"orcs in an ambush position, waiting for the right moment",
"an unknowing Mirkwood elf scout looking out into distance, while an orc is raising his axe behind him, about to strike",
"A blade with a poison/venom coating",
"A dark blade with a poison/venom coating",
"An orc blacksmith forging a blade",
"An orc crafter making a bow",
"An orc lorekeeper in a makeshift lab",
"A group of orcs engaging in construction / building something",
"A chess pawn knocking over a king, representing a bold, audacious, high-risk move",
"The head/portrait of the Great Eagle Gwaihir",
"A river with a clear west-bank and east-bank",
"A man offering a Great Spider some meat",
"A man offering a Great Spider some livestock",
"The nest of Great Spiders being burned/scorched by men",
"something symbolizing self-sufficiency",
"something symbolizing self-sufficiency and autarky",
"A dark flag planted on a piece of territory",
"A dark flag planted on a map, symbolizing the claiming of territory",
"A curved elven blade cutting down a Great Spider's cobweb",
"Two elven warriors fighting in a duel",
"An empty plate alongside a pile of golden coins, symbolizing austerity",
"An elven warrior of Mirkwood driving out an orc and a spider from the forest",
"King Thranduil of Mirkwood expelling dwarven envoys from his halls",
"A rhosgobel rabbit",
"Something that represents deliberately provoking an attack",
"Something that represents staging a border incident",
"A goblin warrior striking a shield, but the shield is way stronger than his attack",
"A small flag or banner on a specific region of a map",
"A medieval soldier holding a shield to both his sides, symbolizing isolation and defense",
"A civilian windmill having been converted into a military forge",
"An Easterling of Rhûn breaking shackles that were keeping his hands bound, representing breaking free",
"An Easterling of Rhûn denouncing Mordor/Sauron",
"closeup of a wainrider of Rhûn, holding the reins of his chariot while making an advanced maneuver",
"Morgoth, the first Dark Lord, in all his glory",
"A banner with bloodstains",
"A medieval soldier pointing downwards, demanding submission",
"A white dove of peace with an arrow shot through it, symbolizing 'no peace'",
"A medieval spearman fighting an axe-wielding dwarf",
"An Easterling soldier from the front wearing boxing gloves, with some bruises/damage from a boxing match, but still ready to strike",
"A hand holding a bloody dagger with a mountain range in the background",
"An Uruk-Hai in full armor making notes on a clipboard, with a Kanban board behind him",
"A rotten/tainted piece of wheat, symbolizing a bad harvest",
"orcs in an ambush position, waiting for the right moment",
"an unknowing Mirkwood elf scout looking out into distance, while an orc is raising his axe behind him, about to strike",
"A blade with a poison/venom coating",
"A dark blade with a poison/venom coating",
"An orc blacksmith forging a blade",
"An orc crafter making a bow",
"An orc lorekeeper in a makeshift lab",
"A group of orcs engaging in construction / building something",
"A chess pawn knocking over a king, representing a bold, audacious, high-risk move",
"The head/portrait of the Great Eagle Gwaihir",
"A river with a clear west-bank and east-bank",
"A man offering a Great Spider some meat",
"A man offering a Great Spider some livestock",
"The nest of Great Spiders being burned/scorched by men",
"something symbolizing self-sufficiency",
"something symbolizing self-sufficiency and autarky",
"A dark flag planted on a piece of territory",
"A dark flag planted on a map, symbolizing the claiming of territory",
"A curved elven blade cutting down a Great Spider's cobweb",
"Two elven warriors fighting in a duel",
"An empty plate alongside a pile of golden coins, symbolizing austerity",
"An elven warrior of Mirkwood driving out an orc and a spider from the forest",
"King Thranduil of Mirkwood expelling dwarven envoys from his halls",
"A rhosgobel rabbit",
"Something that represents deliberately provoking an attack",
"Something that represents staging a border incident",
"A goblin warrior striking a shield, but the shield is way stronger than his attack",
"A small flag or banner on a specific region of a map",
"A medieval soldier holding a shield to both his sides, symbolizing isolation and defense",
"A civilian windmill having been converted into a military forge",
"An Easterling of Rhûn breaking shackles that were keeping his hands bound, representing breaking free",
"An Easterling of Rhûn denouncing Mordor/Sauron",
"closeup of a wainrider of Rhûn, holding the reins of his chariot while making an advanced maneuver",
"Morgoth, the first Dark Lord, in all his glory",
"A banner with bloodstains",
"A medieval soldier pointing downwards, demanding submission",
"A white dove of peace with an arrow shot through it, symbolizing 'no peace'",
"A medieval spearman fighting an axe-wielding dwarf",
"An Easterling soldier from the front wearing boxing gloves, with some bruises/damage from a boxing match, but still ready to strike",
"A hand holding a bloody dagger with a mountain range in the background",
"An Uruk-Hai in full armor making notes on a clipboard, with a Kanban board behind him",
"A rotten/tainted piece of wheat, symbolizing a bad harvest",
"orcs in an ambush position, waiting for the right moment",
"an unknowing Mirkwood elf scout looking out into distance, while an orc is raising his axe behind him, about to strike",
"A blade with a poison/venom coating",
"A dark blade with a poison/venom coating",
"An orc blacksmith forging a blade",
"An orc crafter making a bow",
"An orc lorekeeper in a makeshift lab",
"A group of orcs engaging in construction / building something",
"A chess pawn knocking over a king, representing a bold, audacious, high-risk move",
"The head/portrait of the Great Eagle Gwaihir",
"A river with a clear west-bank and east-bank",
"A man offering a Great Spider some meat",
"A man offering a Great Spider some livestock",
"The nest of Great Spiders being burned/scorched by men",
"something symbolizing self-sufficiency",
"something symbolizing self-sufficiency and autarky",
"A dark flag planted on a piece of territory",
"A dark flag planted on a map, symbolizing the claiming of territory",
"A curved elven blade cutting down a Great Spider's cobweb",
"Two elven warriors fighting in a duel",
"An empty plate alongside a pile of golden coins, symbolizing austerity",
"An elven warrior of Mirkwood driving out an orc and a spider from the forest",
"King Thranduil of Mirkwood expelling dwarven envoys from his halls",
"A rhosgobel rabbit",
"Something that represents deliberately provoking an attack",
"Something that represents staging a border incident",
"A goblin warrior striking a shield, but the shield is way stronger than his attack",
"A small flag or banner on a specific region of a map",
"A medieval soldier holding a shield to both his sides, symbolizing isolation and defense",
"A civilian windmill having been converted into a military forge",
"An Easterling of Rhûn breaking shackles that were keeping his hands bound, representing breaking free",
"An Easterling of Rhûn denouncing Mordor/Sauron",
"closeup of a wainrider of Rhûn, holding the reins of his chariot while making an advanced maneuver",
"Morgoth, the first Dark Lord, in all his glory",
"A banner with bloodstains",
"A medieval soldier pointing downwards, demanding submission",
"A white dove of peace with an arrow shot through it, symbolizing 'no peace'",
"A medieval spearman fighting an axe-wielding dwarf",
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