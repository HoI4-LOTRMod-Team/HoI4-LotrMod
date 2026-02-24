

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/lratca3ktf8s", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/e2vqaxlxnpy6", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/q0uidxakun2p", 
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
prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. You will be generating generic decorative assets for various icons and UI components, such as ribbons, dividers, decorations etc.
I've attached some example images of such elements as a style guide.

The final icon will be displayed at a small size. To ensure clarity at this scale: Focus on a **strong, recognizable silhouette**.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Prompt to generate:** PROMPT
"""


# # GENERIC ASSETS
# prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. You will be generating generic assets for various icons and UI components.
# I've attached some example images of such elements as a style guide.

# The final icon will be displayed at a small size. To ensure clarity at this scale: Focus on a **strong, recognizable silhouette**.

# **Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

# **Prompt to generate:** PROMPT
# """


prompt_list = [
    "A tattered parchment ribbon banner, fantasy UI element, worn edges, dark shading, HOI4 focus icon style",
    "An ornate golden metallic banner with elven filigree, fantasy UI asset, embossed",
    "A heavy iron ribbon banner with dwarven geometric patterns, dark metal UI element",
    "A torn red cloth pennant hanging from a dark steel rod, orcish UI asset",
    "A smooth silver scroll unrolling, elegant fantasy UI background element",
    "A bronze scroll piece with jagged edges, worn texture, UI element",
    "A dark leather banner stretched between two bone spikes, fantasy UI",
    "A silken green ribbon with a golden leaf motif, elven UI element",
    "A stone carved ribbon banner, dwarven UI asset, heavy shadows",
    "A rusted iron chain linking two metallic plates, UI background element",
    "A glowing ethereal blue ribbon, magic fantasy UI asset",
    "A burned parchment scrap, dark fantasy UI background, ashen edges",
    "A pristine white marble banner with gold trim, Gondor style UI element",
    "A weathered wood plank sign with iron rivets, Rohan style UI element",
    "A braided gold and silver wire banner, elegant UI asset, metallic shine",
    "Stylized bronze eagle wings spread open, metallic UI icon, HOI4 style",
    "Dark jagged metallic bat wings, Mordor style UI asset, rusted iron",
    "Elegant sweeping silver swan wings, elven UI element, polished",
    "Stone carved raven wings, heavy and weathered UI asset",
    "Golden interlocking geometric wings, dwarven UI motif, embossed",
    "White feathered angelic wings with a soft glow, fantasy UI",
    "Iron mechanical looking wings, dark fantasy UI element",
    "A single stylized golden feather, embossed UI asset",
    "A pair of ashen gray moth wings, dark fantasy UI icon",
    "Sweeping copper falcon wings, worn metallic UI asset, verdigris",
    "A stylized cluster of dark iron flames, Mordor style UI element",
    "A burst of golden ethereal light rays, fantasy UI background",
    "A silver multi-pointed star, elven style UI icon, glowing center",
    "A jagged crack glowing with red magma, dark fantasy UI asset",
    "A stylized swirling water drop in blue glass, fantasy UI element",
    "A cluster of glowing green magic sparks, UI background element",
    "A stylized heavy stone anvil, dwarven UI icon, carved details",
    "A swirling vortex of shadows and smoke, dark magic UI asset",
    "A brilliant white sunburst, Rohan style UI background, metallic gold",
    "A stylized frozen ice crystal, fantasy UI element, sharp edges",
    "A blank round wooden shield with an iron rim, fantasy UI background",
    "An ornate silver kite shield with blank center, elven UI asset",
    "A heavy octagonal bronze shield with runes, dwarven UI element",
    "A jagged rusted iron shield with spikes, orcish UI background",
    "A blank white marble crest with gold trim, Gondor style UI element",
    "A dark steel triangular crest with a red glowing center, UI asset",
    "A polished gold circular emblem with a floral border, UI background",
    "A weathered leather buckler shield, fantasy UI element",
    "A blank obsidian shield with silver veins, dark fantasy UI",
    "A tall slender elven shield, silver and blue, UI background",
    "Two crossed silver elven swords, decorative UI background, metallic",
    "Two crossed heavy iron axes, dwarven UI background element",
    "A broken steel longsword, worn fantasy UI icon",
    "A jagged rusted scimitar, dark fantasy UI element, bloodstained iron",
    "A cluster of bronze spear tips pointing upwards, UI asset",
    "Two crossed wooden longbows, elven UI background",
    "A glowing magical dagger, fantasy UI element",
    "A spiked iron mace head, dark fantasy UI asset",
    "Two crossed golden tridents, UI background element",
    "A stylized bundle of silver arrows, UI icon, embossed",
    "A stylized silver tree with curved branches, Gondor style UI element",
    "A golden stylized oak leaf, elven UI asset, filigree",
    "A tangled border of dark thorny vines, Mordor style UI frame",
    "A border of elegant silver ivy leaves, elven UI frame",
    "A cluster of golden wheat, Rohan style UI element",
    "A twisted dead tree branch, dark fantasy UI background",
    "A blooming white flower with a glowing center, magic UI asset",
    "A stylized pinecone in bronze, UI element, metallic",
    "Deep stone roots twisting together, dwarven UI background",
    "A single glowing silver fern leaf, fantasy UI icon",
    "A jagged iron crown with a red jewel, dark fantasy UI element",
    "An elegant silver circlet with a clear gem, elven UI asset",
    "A heavy blocky gold crown, dwarven UI icon, carved",
    "A plain glowing golden ring, fantasy UI element, smooth gold",
    "A winged silver helmet crest, Gondor style UI asset",
    "A horse-head shaped bronze helm crest, Rohan style UI element",
    "A twisted ring of dark magic, Mordor style UI asset, jagged metal",
    "A laurel wreath of golden leaves, UI background element",
    "A stylized crown of white tree branches, UI icon",
    "A spiked iron collar, dark fantasy UI element",
    "A carved stone tablet with glowing blue runes, dwarven UI asset",
    "A circular border of interlocking elven knots, silver UI frame",
    "A jagged black iron circular border, dark fantasy UI frame",
    "A square frame made of heavily riveted bronze, dwarven UI element",
    "A stylized golden archway, fantasy UI background",
    "A dark stone pedestal with glowing red cracks, UI base element",
    "A polished white marble column base, UI pedestal",
    "A complex geometric gold and iron gear, dwarven UI asset",
    "A swirling silver galaxy motif, magic UI background",
    "A border of stylized bronze scales, dragon UI element",
    "A carved wooden plaque with knotwork, Rohan UI base",
    "A glowing ethereal magic circle, fantasy UI background",
    "A rusted iron cage grating, dark fantasy UI background",
    "A silver moon crescent, elven UI icon",
    "A stylized golden sunburst medallion, UI asset",
    "A pair of bronze lion heads, decorative UI flourish",
    "A dark iron skull motif, dark fantasy UI element",
    "A cascading waterfall of silver light, UI background",
    "A pile of gold coins and gems, dwarven UI asset",
    "A scattering of black ash and embers, Mordor UI background",
    "A stylized glowing blue eye, magic UI element",
    "A red glowing molten metal puddle, UI base element",
    "A silver hourglass with glowing sand, fantasy UI icon",
    "A bronze compass rose, fantasy UI element, worn",
    "A pair of silver clasps with elven script, UI flourish"
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