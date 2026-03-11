

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/bnl9jn2d0h3w", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/n3r7wtsmouj4", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/tmzzezngsupa", 
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
"A rustic spear and a wooden shield crossed together, with a rallying horn in the foreground",
"A strategy map with wooden markers being moved by a commanding hand",
"A commanding officer in rugged armor addressing a disciplined row of Hill-men soldiers",
"A dusty, ancient scroll unfurled next to a candle, showing old battle formations",
"A rugged tent interior with a tactical map and a sword resting on the table",
"A gleaming sword striking an anvil with sparks flying, symbolizing refined warfare",
"A shiny new steel broadsword layered over a cracked, older iron blade",
"A wild Hill-man warrior shaking hands with a polished Dunedain ranger",
"A cloaked Dunedain ranger aiming a longbow from the shadows of a forest",
"Dozens of crude spears raised high against a misty mountain backdrop",
"A majestic eagle soaring high above the Misty Mountains",
"A giant eagle's talons gripping the craggy peak of a mountain",
"The silhouette of a great eagle dropping a payload over a battlefield",
"A broken troll's club lying in a sunlit forest clearing",
"A wooden surveying tripod and a coiled rope resting on cleared earth",
"A stone workshop with a large waterwheel and smoke rising from a chimney",
"A sturdy stone bridge crossing a wild, rushing river",
"A stack of freshly cut timber next to a large forester's axe",
"A dirt road winding up a steep, rocky hillside",
"A weaver's loom and a blacksmith's anvil side by side",
"A glowing forge with multiple iron swords heating in the coals",
"A large wooden windmill on a grassy hill",
"A bustling quarry with carts full of mined stone and ores",
"A heavy iron anvil with a massive forging hammer resting on top",
"Rows of newly forged shields and spears emerging from a dark factory",
"An astrolabe, a magnifying glass, and an open book on a wooden desk",
"A ranger's arrow piercing a troll's skull in a marshy moor",
"A Rhudaur banner planted firmly in the rocky soil of the moors",
"A deep mine entrance with a cart full of dark iron ore",
"A stone pathway being laid down through a treacherous swamp",
"A rustic village transforming into a bustling trade hub with carts and workers",
"A crossroads signpost with three arrows pointing in different directions, shrouded in mist",
"A dark, iron-wrought crown glowing with an eerie green light",
"A silver star emblem representing Arnor, shining over a diplomatic scroll",
"A large wooden table surrounded by empty, rustic chieftain chairs",
"The white tree of Arnor intertwined with the rugged symbols of Rhudaur",
"A pair of hands holding up a neutral, blank grey shield",
"A shadowy figure with red eyes looming over the hills of Rhudaur",
"A thick stone wall with wooden palisades blocking a mountain pass",
"Two hands exchanging a loaf of bread and a silver coin",
"A spyglass resting on a map of Eriador",
"A parchment letter sealed with wax being carried by a messenger bird",
"A heavily fortified wooden keep atop a steep, defensible hill",
"A line of spiked barricades facing towards a dark, frozen wasteland",
"A watchtower overlooking a river delta and forest",
"Elven arrows stuck into the outer side of a wooden shield",
"A lone scholar reading a glowing tome in a dark, quiet room",
"A group of Dunedain rangers standing together in a tight, disciplined formation",
"A bloody dagger struck through a treaty parchment",
"A shadowy hand sweeping miniature wooden figures off a map",
"A wild chieftain blowing a large animal horn on a mountaintop",
"A wanted poster showing a Dunedain ranger with a dagger through it",
"A bag of gold coins and a dark amulet offered to a shadowy ranger",
"The flaming Eye of Sauron reflected in a dark pool of water",
"The spiked iron mask of the Witch-king looming in a blizzard",
"A single, bright torch burning proudly against a backdrop of encroaching shadows",
"A ruined stone watchtower on a hill, with a red banner being raised",
"A gauntleted hand slamming down onto a map of Amon Sul",
"A newly fortified Weathertop, bustling with Hill-men guards",
"A dark palantir glowing with residual, cracking magical energy",
"An orcish scimitar crossed with a Hill-man's spear",
"A broken iron crown tossed into the mud",
"Dark storm clouds gathering over the jagged fortress of Carn Dum",
"A Hill-man chieftain sitting upon a throne of dark iron",
"Propaganda leaflets scattered across a medieval street",
"A Dunedain knight and a Hill-man warrior sparring together",
"A puppet on strings shaped like a Rhudaur warrior, manipulated by a spectral hand",
"A broken elven spear and an Arnorian shield burning in a bonfire",
"An emissary presenting a heavy iron chain to a defeated noble",
"A shattered silver star emblem under a heavy leather boot",
"A pair of crude iron shackles linked together",
"A hobbit's round door being smashed open by a heavy mace",
"A grand, dark-stone monument of a Numenorean king overlooking Eriador",
"The white tree of Gondor wilting under a dark, suffocating mist",
"A golden chalice and a silver sword resting on a pure white cloth",
"Two angry men being separated by a wise leader holding a staff",
"A silver star beacon lit upon a high hill, summoning the Dunedain",
"A Dunedain ranger receiving a masterfully crafted new sword",
"A Hill-man being handed a proper steel sword to replace his club",
"The White Tower of Ecthelion shining in the distance",
"A crown of Gondor and a silver star of Arnor side by side",
"A vast hall filled with ancient books and glowing parchment",
"Two armored hands clasping in a strong, brotherly handshake",
"A spectral figure pointing a skeletal finger forward, leading the way",
"A rusted, dark weapon being reforged into a shining, noble blade",
"An elegant elven ring sitting next to a diplomatic scroll",
"An elven gateway opening, with light spilling out into the dark hills",
"A ruler wearing a simple circlet, reading from a book of laws",
"A massive shield sheltering a group of frightened peasants",
"A sharp dagger cutting away the blackened, diseased part of an apple",
"A white dove landing on a rusted, abandoned sword",
"A collection of beautiful pottery, scrolls, and agricultural tools",
"A sun rising over a peaceful, green valley filled with crops",
"Two rangers whispering over an ancient map lit by a lantern",
"A recruitment poster featuring both a Rhudaur warrior and an Arthedain soldier",
"A soldier studying a series of muddy footprints in a marsh",
"A pickaxe clearing away thorny, twisted briars from a hillside",
"A troll turned to stone by the morning sun, covered in moss",
"A heavily armed rider on a sturdy mountain horse",
"A small, sturdy fishing boat moored in a marshy wetland",
"A well-paved stone road leading straight towards a grand city on a hill",
"A merchant's cart loaded with barrels and crates, traveling on a safe road",
"A group of recruits practicing archery in a dense, hilly woodland",
"A ranger's cloak blending perfectly into the bark of a thick tree",
"A long line of pack mules and wagons laden with goods",
"Cozy, fortified cabins built into the side of a snowy mountain",
"A golden chest left on a high, precarious mountain ledge",
"A heavy iron grate barricading a dark cave entrance",
"A solitary traveler climbing a snowy pass, looking towards a green valley",
"An ancient stone pillar carved with the history of Numenor",
"A messenger arriving at a peaceful riverside settlement",
"A lone watchman standing on a high crag, overlooking misty valleys",
"A heavy castle door securely bolted shut from the inside",
"A scale weighing a small portion of grain against a stone weight",
"An hourglass with sand slowly falling, sitting next to a growing sapling",
"A dagger pinning a strategic map, with only a small area circled",
"A compass and a worn map of far-off lands",
"Open wooden gates welcoming a line of weary travelers carrying bundles",
"A bustling crowd of workers with pickaxes and hammers heading to a site",
"A dark eclipse covering the sun over the hills of Rhudaur",
"A warrior kneeling and offering his sword to a dark, cloaked figure",
"The banners of Rhudaur and Angmar flying side by side in a storm",
"A burned grievance treaty blowing away in the wind",
"An army of Hill-men charging across a river towards Arnorian shields",
"A spear shattering the silver star shield of Arthedain",
"A Rhudaur official stamping a document over an old Arnorian crest",
"Replacing the banners on a Cardolan keep with the colors of Rhudaur",
"A flaming arrow striking a Cardolan watchtower",
"A hidden mountain pass in the snow, with an army silently marching through",
"A hunter skinning a beast in the wild, totally self-reliant",
"A burning village with warriors carrying away chests of loot",
"A human hand and a clawed goblin hand exchanging gold for a map",
"A horde of warriors rushing down a steep, rocky slope into a valley",
"A beautiful elven statue being toppled by a thick rope",
"The elegant waterfalls and bridges of Rivendell burning and ruined",
"An elven forge now churning out crude, dark iron weapons",
"A crude wooden watchtower built right in the middle of elven ruins",
"Three dark rings interlocked in a symbol of malevolent alliance",
"Crates of black iron weapons bearing the mark of the Red Eye",
"A chest overflowing with dark jewels and a sinister glowing weapon",
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