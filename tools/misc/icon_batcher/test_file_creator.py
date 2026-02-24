

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/bmwno9zm6jhj", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/tv80v7vhy9rl", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/s6863omf5d5y", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/q8qtp0mm1ra9", 
                        "mime_type": "image/png"
                    }
                },
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

prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. You will be generating images of laurels, decorations and frames for various icons and UI components.
I've attached some example images of such elements as a style guide.

The final icon will be displayed at a small size. To ensure clarity at this scale: Focus on a **strong, recognizable silhouette**.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Prompt to generate:** PROMPT
"""


prompt_list = [
"Golden laurel wreath with glowing white tree blossoms, dark background, UI icon asset",
"Circular frame made of braided silver and starlight, elegant elven UI element, dark background",
"Jagged black iron ring glowing with intense red heat, dark background, Mordor UI frame",
"Heavy bronze octagonal frame with carved dwarven geometric runes, dark background, UI asset",
"Circular frame made of interlaced golden horsehair and green leather, Rohan UI element",
"Industrial iron gear forming a circular frame, oily and dark, Isengard UI asset",
"Wreath made of blackened, charred branches with glowing embers, dark background, UI element",
"Elegant silver mithril vine forming a circular border with small blue gems, elven UI frame",
"Wreath of golden autumn leaves, Lothlorien style, dark background, UI icon asset",
"Gondorian white marble archway frame with silver trim, symmetrical, UI element",
"Ring of heavy, rusty spiked chains, dark fantasy UI frame, dark background",
"Golden sunburst frame with a flowing green banner at the bottom, UI asset",
"Wreath of pale, glowing white flowers and silver leaves, dark background, UI element",
"Dark obsidian jagged ring frame emitting faint white smoke, dark background, UI asset",
"Frame made of dwarven gold coins and geometric stone blocks, UI element",
"Winged silver swan motif forming a circular border, dark background, UI frame",
"Rusty iron banner ribbon with sharp, jagged edges, dark fantasy UI element",
"Golden victory ribbon with a tattered, ancient appearance, vintage fantasy UI",
"Circular frame of intertwined thorny black vines, dark background, UI asset",
"Bronze laurel wreath crossed with miniature dwarven axes at the base, UI element",
"Frame made of thick, knotted hemp rope and weathered wood, Hobbit style UI",
"Wreath of golden wheat and green vines, Shire agricultural UI frame, dark background",
"Silver ribbon scrolling horizontally, elegant elvish script faintly visible, UI asset",
"Parchment scroll banner with scorched edges and a red wax seal, UI element",
"Circular border of glowing red volcanic rock and magma, dark background, UI frame",
"Iron ring surrounded by green, poisonous-looking mist, dark background, UI asset",
"Wreath made of shattered weapons and broken arrows, dark fantasy UI frame",
"Gleaming silver shield border with a gold star at the crest, UI element",
"Circular frame made of tightly woven chainmail, dark background, UI asset",
"Banner made of stretched, dark leather with crude iron rivets, Orcish UI element",
"Wreath of pale moonlight and mist, ethereal UI frame, dark background",
"Heavy stone circular frame with glowing blue dwarven runes, dark background",
"Frame of overlapping iron plates, like heavy armor, dark background, UI asset",
"Golden ribbon banner folded symmetrically, royal Gondor style UI element",
"Circular border made of intertwined snake skeletons, dark background, UI frame",
"Wreath of pristine white swan feathers, dark background, UI icon asset",
"Bronze circular frame with a hammered, imperfect texture, UI element",
"Ribbon made of flowing, ethereal blue water, magical UI banner asset",
"Jagged crown of black iron spikes forming a circular frame, dark background",
"Frame made of polished wooden branches with green budding leaves, UI asset",
"Circular border of crushed ice and frost, dark background, UI frame",
"Wreath of dark, withered, twisted roots, dark fantasy UI element",
"Banner made of fine, shimmering elven silk, silver and blue, UI asset",
"Circular frame made of stacked, crude Orcish scimitars, dark background",
"Golden frame resembling a massive ring with faint fiery script, UI element",
"Wreath of bright, blooming athelas flowers and green leaves, dark background",
"Thick iron chain frame broken at the top, dark fantasy UI asset",
"Circular border of polished copper with geometric dwarven cuts, dark background",
"Banner of dark crimson cloth with a jagged black border, UI element",
"Frame made of pale, smooth bone and dark leather bindings, UI asset",
"Wreath of glowing golden embers and ash, dark background, UI element",
"Circular border of intricately carved white ivory, dark background, UI frame",
"Ribbon banner made of woven gold threads, luxurious UI asset",
"Frame made of ancient, moss-covered stone blocks, dark background",
"Wreath of sharp, metallic bladed leaves, dark fantasy UI element",
"Circular frame of swirling, dark shadow magic, UI asset, dark background",
"Banner made of crisp, white linen with a silver trim, UI element",
"Frame of interlocking bronze rings, dwarven chainmail style, UI asset",
"Wreath of bright yellow sunflowers and green grass, Hobbit UI frame",
"Circular border of dark, oily water and rusted metal, dark background",
"Jagged piece of dark iron bent into a crude banner shape, UI element",
"Frame made of polished green jade with silver accents, UI asset",
"Wreath of red maple leaves and golden acorns, dark background, UI frame",
"Circular border of glowing yellow eyes peering from dark shadows, UI asset",
"Banner of tattered, mud-stained green cloth, ranger style UI element",
"Frame made of intricately folded origami-like metal plates, UI asset",
"Wreath of glowing blue mushrooms and dark cave crystals, dark background",
"Circular border of burning coal and twisted iron wire, UI frame",
"Ribbon banner made of pale, translucent parchment, ethereal UI asset",
"Frame of large, rough-hewn diamonds and dark stone, Dwarven UI element",
"Wreath of black feathers and silver talons, dark background, UI frame",
"Circular border of swirling golden sand, dark background, UI asset",
"Banner made of overlapping brown dragon scales, dark fantasy UI element",
"Frame made of petrified wood and amber, dark background, UI asset",
"Wreath of blooming red roses and sharp thorns, UI frame",
"Circular border of ancient, cracked pottery shards, dark background",
"Ribbon banner made of glowing white light, ethereal UI element",
"Frame of rusted iron gears and snapping springs, goblin UI asset",
"Wreath of dark purple thistles and silver wire, dark background, UI frame",
"Circular border of floating, glowing runestones, dark background",
"Banner of dark velvet with gold fringe tassels, regal UI element",
"Frame made of massive, curved mammoth tusks, dark background, UI asset",
"Wreath of sea-green kelp and pale seashells, nautical UI frame",
"Circular border of dripping, glowing green venom, dark background, UI asset",
"Ribbon banner made of woven spider silk, dark fantasy UI element",
"Frame of highly polished obsidian mirrors, dark background, UI asset",
"Wreath of vibrant green ferns and moss, dark background, UI frame",
"Circular border of burning white holy fire, UI asset, dark background",
"Banner of stiff, painted canvas with faded geometric patterns, UI element",
"Frame made of interlocking golden keys, dark background, UI asset",
"Wreath of pale, glowing crystals and silver dust, dark background, UI frame",
"Circular border of thick, bubbling black tar, dark background, UI asset",
"Ribbon banner made of hammered silver foil, UI element",
"Frame of ancient, weather-beaten bronze shields, dark background, UI asset",
"Wreath of bright orange autumn leaves and twigs, UI frame",
"Circular border of swirling, dark storm clouds and lightning, UI asset",
"Banner made of animal fur and leather straps, wildmen UI element",
"Frame made of overlapping, razor-sharp flint stones, dark background, UI asset",
"Wreath of golden apple blossoms and green leaves, UI frame",
"Circular border of intricately carved red mahogany wood, UI asset"
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