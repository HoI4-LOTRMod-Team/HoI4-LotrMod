

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/gvlhow10pktc", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/iocmrhca9hs7", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/5f7woi7rb935", 
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
"A compass resting on a worn map of eastern lands",
"A vast formation of Easterling spearmen marching in unison",
"Gold coins being poured into a large wooden chariot wheel",
"A swift, lightly armored horseman riding across the plains",
"A heavily armored warhorse covered in scale mail",
"A large, menacing wooden ballista loaded with a heavy bolt",
"A recurve bow crossing a quiver full of arrows",
"A heavy iron-reinforced crossbow",
"A miner's pickaxe striking rich iron ore in a dark cave",
"A sturdy logging axe embedded in a thick mountain pine tree",
"A glowing hot anvil struck by a heavy blacksmith's hammer",
"Hands exchanging a large purse of golden coins",
"Brick factory chimneys rising against a cold northern sky",
"Paved stone roads and industrial gears",
"Heavy construction tools crossed over a stone blueprint",
"A bustling eastern market stall filled with exotic spices and fabrics",
"Bundles of golden wheat next to grazing livestock",
"Neatly organized rows of military tents and wooden training dummies",
"Tall bookshelves filled with ancient scrolls and thick leather tomes",
"A winding dirt road cutting through mountainous terrain towards the south",
"Brass merchant scales balancing gold and goods",
"A large fishing net overflowing with silver fish",
"A massive stone silo filled to the brim with grain",
"A grand dome of a scholarly institution surrounded by star charts",
"A lantern illuminating a snowy mountain pass",
"A sinister black iron crown glowing with a dark aura",
"An open book of laws next to a united tribal banner",
"A heavy iron boot crushing a rival clan's shield",
"Two Easterling warriors shaking hands beneath a golden light",
"A shadowy, hooded figure being banished by a bright light",
"The dark tower of Barad-dûr looming over a kneeling Easterling",
"A cruel whip raised over cowering citizens in the shadows",
"A fierce ringwraith wearing an Easterling helm, commanding an army",
"A massive, heavily armored troll roaring in battle",
"A torn banner depicting Easterlings fighting each other in a civil war",
"The Flaming Eye of Sauron gazing over a scroll of war",
"A magnificent golden crown symbolizing a newly forged empire",
"A map with aggressive red arrows pointing eastward",
"A dark missive sealed with the fiery eye of Sauron",
"Wooden crates overflowing with freshly forged weapons and armor",
"Endless ranks of heavily armored soldiers under a dark sky",
"A Rhunian sword piercing through a tribal map",
"Rhunian and tribal shields overlapping in unity",
"Massive siege engines firing upon dwarven stone gates",
"Crates of supplies being handed over to an orcish warlord",
"An Easterling helmet looking resolutely towards snowy mountains",
"A gauntleted hand snatching gold and grapes",
"Elven woodland burning under the march of an invading army",
"An emissary presenting a chest of gold to a desert warlord",
"A fortified wall of stakes overlooking a vast desert",
"The banners of Rhun planted firmly in the sand dunes of Khand",
"Gold coins being panned and invested in a desert settlement",
"A colossal Mûmakil war elephant towering over the battlefield",
"An Easterling scimitar slashing through a horse-lord's shield",
"A beautiful chalice of wine being shattered by an iron mace",
"A harsh treaty document nailed to a wall with a dagger",
"Industrial smokestacks replacing rolling vineyards",
"Lush, fruitful grapevines growing on trellises in the sun",
"An iron boot stepping heavily on a smoldering torch",
"A puppet ruler manipulated by shadowy strings from above",
"A Rhunian diplomat handing a treaty to a defiant horse-lord",
"Easterling halberds clashing violently with cavalry spears",
"A hollow-eyed king wearing a tarnished crown, controlled by shadowy strings",
"Plows and shovels turning wild plains into organized farmland",
"An imposing coastal bastion built of dark stone",
"Scouts unfurling a map over a newly constructed road",
"A tall wooden watchtower scanning the plains",
"Merchant carts laden with wine and grain traversing a road",
"A dark iron chain breaking off a golden Easterling bracer",
"A torn parchment bearing the mark of Sauron",
"Shadowy whispers surrounding a confused Easterling helm",
"Two figures in deep blue robes wielding glowing magical staffs",
"A passionate speaker rallying a crowd of Easterling peasants",
"A localized map region glowing with rebellious fire",
"Eastern banners raising in defiance of their dark lords",
"An Easterling officer turning his blade away from his commander",
"Pitchforks and torches gathered in a secretive revolt",
"Wooden crates being covered by a large tarp in a hidden cave",
"A secret forge operating under the cover of night",
"Miners working quietly with muffled pickaxes in the dark",
"A chariot wheel with its spokes being sawed halfway through",
"Civilians putting on hidden armor in the shadows",
"Fierce desert warriors wielding curved swords in secret",
"Eastern militiamen holding crude spears and shields",
"Steppe fighters practicing with bows and light armor",
"A massive rack overflowing with sharp spears",
"Rows of war chariots hidden in a large barn",
"A classic Easterling Wainrider driving a fierce chariot",
"A blueprint of an upgraded, lethal chariot chassis",
"An archer firing a bow precisely from a speeding chariot",
"A master artisan carving intricate designs into a war wagon",
"Gold coins falling onto a pile of raw iron and wood",
"An experienced warlord pointing at a tactical war map",
"A tribal Balchoth warrior painted fiercely for war",
"Lightly armored runners with javelins moving swiftly",
"A dense formation of archers drawing their bows in unison",
"Elite chariot riders wearing heavy scale armor",
"Scales balancing a chariot wheel and an infantry shield",
"A massive heavy chariot reinforced with thick iron plates",
"Guards aggressively arresting a figure in blue robes",
"A majestic leader addressing a crowd of loyal charioteers",
"A glowing magical amulet being crushed to dust",
"Soldiers marching through a desert town imposing strict order",
"Guards patrolling the streets of a major Easterling city",
"Military checkpoints established in a frontier settlement",
"An Easterling banner being raised over snowy northern lands",
"A lone warrior standing defiantly against a dark storm",
"An emissary requesting aid from Dorwinion guards",
"Factories producing weapons at a frantic pace for the rebellion",
"Heavy anvils and hammers working continuously to build industry",
"Rebellious soldiers rallying behind two blue-clad wizards",
"A mystical blue light illuminating a strategic military map",
"A peace treaty being signed on a nomadic saddle",
"A formal tripartite pact signed in a grand Rhunian hall",
"A rebellious army marching towards the dark clouds of Mordor",
"A torn Easterling flag, split in two by a sword",
"A firm handshake between an Easterling and a Dorwinion merchant",
"Massive stockpiles of newly forged rebel weapons",
"Expansion of massive industrial complexes across the plains",
"A rebel general inspecting troops preparing for imminent battle",
"A diplomat observing a tribal Logath camp from a distance",
"A gauntleted fist slamming aggressively onto a negotiation table",
"A map being carved up with an Easterling dagger",
"Tribal Logath chiefs bowing to a powerful Rhunian envoy",
"Two different administrative seals melting into one unified crest",
"Heavily armored guards forcefully subduing a rioter",
"Three large red arrows pointing west on a parchment map",
"A Rhunian soldier throwing an insult at dwarven and human shields",
"A dark, overgrown road leading into a foreboding elven forest",
"An Easterling general drawing his own sword in frustration",
"Soldiers blending into the foliage, holding throwing axes",
"Looted treasure chests piling up in a victorious war camp",
"Soldiers wading through murky, fog-covered swampland",
"A spyglass focusing intently on the spires of the city of Dale",
"Border stakes being aggressively moved forward into new lands",
"An endless horde of Easterlings marching under a conquering banner",
"Settlers building wooden houses in a newly conquered territory",
"An Easterling looking down at a sturdy dwarven emissary",
"Heavy stone barricades facing the ash wastes of Mordor",
"A massive shield wall standing firm against a red shadow",
"Silhouetted nobles whispering treason behind grand palace pillars",
"A poisoned dagger hidden behind a nobleman's back",
"A pompous commander being stripped of his medals",
"Sand rapidly falling through a golden hourglass",
"Guards dragging a screaming bureaucrat out of a throne room",
"A pouch of coins being slipped to a merchant from Esgaroth",
"Rare gemstones offered on a velvet pillow to a dwarf",
"Scales of justice balancing perfectly over a peaceful city",
"Doves flying outward carrying diplomatic messages",
"A scarred warrior sharpening a blade with a hateful glare",
"A Rhunian envoy bowing before the King of Dale",
"New recruits training rigorously in a courtyard",
"The banners of the rebellion and the Logath tribes flying together",
"A peace treaty being thrown into a blazing fire",
"Scholars blowing dust off old blueprints and books",
"An Easterling rebel standing shoulder to shoulder with dwarven warriors",
"A fearsome spiked barricade meant to ward off invaders",
"Disciplined spearmen holding a tight, unbreakable phalanx",
"Neatly organized scrolls and an inkwell on a desk",
"A bright flame burning atop a high tower, cutting through the dark",
"A convoy of supply wagons rolling down a secured road",
"A glowing magnifying glass over ancient texts",
"A galloping Easterling horse with elaborate barding",
"A military manual opened to a page showing flanking maneuvers",
"An advanced military textbook with glowing tactical lines",
"A masterfully forged new scimitar next to an old, rusted one",
"A warrior wearing a dust-veil, adapted for desert combat",
"Tribal wise men sharing knowledge around a fire",
"A loyalist sword striking down a rebel banner",
"A secretive meeting with dark-haired elves in a twilight forest",
"A towering red mountain range secured by a fortress",
"Eastern nomads seamlessly joining a rebel army",
"Grain being seized and replaced with iron ore",
"An intimidating envoy holding an ultimatum scroll",
"A Khandish leader demanding freedom from a Haradrim master",
"Exchanging Rhunian steel for Variag horses",
"A contract stamped over a map of Khand's resources",
"A heavy chest of Mordor gold given as payment",
"The banner of Rhun flying alongside the flaming eye of Sauron",
"A grand table where eastern warlords unite under one symbol"
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