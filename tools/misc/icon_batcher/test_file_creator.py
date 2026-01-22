

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/rd3lgpq4xta7", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/xtwln2wql745", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/1pxvtlpmx0t3", 
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

random_insert = """This icon is for Rohan."""

random_chance = 0.5

prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. 
I've attached some example images as a style guide, which would correspond to the following prompts:
"A trio of medieval soldiers with leather armor and swords",
"A red medieval flag waving in the wind",
"Faramir and Eowyn from LOTR holding hands while getting wed".

**Artistic Style (Reference Examples):**
Follow therealistic, hand-illustrated and cinematic style of these examples. Avoid flat colors, black outlines, and cartoon aesthetics.
$RANDOM$

**Readability & Scale:**
The final icon will be displayed at a small size (200x200). To ensure clarity at this scale:
- Focus on a **strong, recognizable silhouette**.
- Use **bold primary forms** to define the shape.
- Prioritize the "feel" of the texture over microscopic details that would disappear when shrunk.
- Use a realistic looking style, but avoid excessive detail that would clutter the small icon.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Subject to generate:** PROMPT
"""


prompt_list = [
"A worn Rohan banner waving against a stormy sky, stylized",
"Iron ore and a pickaxe resting on a rock",
"A hooded scout peering through binoculars at snowy mountain peaks",
"Two armored hands clasping in agreement, a sword in the background",
"An ancient Rohan helmet resting on a wooden table",
"An open book with a candle casting light on the pages",
"A stone statue of a Rohirrim warrior standing firm against wind",
"A gavel striking a document on a desk",
"A map of Rohan with a wax seal being placed on a region",
"A horse-shaped weathervane turning in the wind",
"A pile of cut timber logs with a lumberjack axe",
"An hourglass with sand turning into industrial gears",
"A stylized silhouette of a factory with smoke stacks",
"A balanced scale holding a sword and a blueprint",
"A blacksmith hammer striking a glowing sword on an anvil",
"A beaker with bubbling green liquid and a magnifying glass",
"Tall bookshelves filled with ancient scrolls and tomes",
"A cobblestone road winding towards distant mountains",
"Ancient stone fortifications built into a cliffside",
"Molten metal being poured in a dark mountain forge",
"A pale man with black hair whispering into an ear, stylized shadows",
"A hand passing a bag of gold coins under a table",
"A hand knocking over a knight chess piece",
"A spyglass focused on a Mallorn leaf",
"A simple gold ring resting on a tactical map",
"Hobbit footprints in the mud being examined",
"Spears hidden in tall grass waiting to strike",
"The White Hand of Saruman painted on a shield",
"A dark looming shadow over a frightened village",
"An old king sitting slumped and alone on a throne in shadow",
"A royal shield lying broken in the mud",
"A warrior walking away into the distance, silhouette",
"A council table surrounded by shadowy figures",
"A golden scale perfectly balanced",
"Several regional banners of Rohan displayed together",
"A pile of gold coins with a broken chain on top",
"Three shields interlocking in a defensive formation",
"A heavy wooden gate being shut and barred",
"A soldier with a spear standing guard at sunset",
"A green flag with a white horse planted on a hilltop",
"The stone wall of Helms Deep with a tower",
"A stone culvert reinforced with iron bars",
"The Golden Hall of Meduseld shining in the sun",
"Sparks flying from a large industrial anvil",
"A map of Western Rohan with fortifications marked",
"A castle blueprint laid over a grassy field",
"A wagon loaded with supplies moving away from a burning village",
"A round wooden table illuminated by a bright light",
"A wizard in a grey cloak holding a staff appearing in a doorway",
"Great wooden doors swinging open to reveal a bright light",
"A sword cutting through tangled thorny vines",
"A hand pointing authoritatively towards an open gate",
"Horses carrying supplies given to travelers",
"A Rohirrim shield protecting a small gold ring",
"Iron shackles lying on a wooden floor",
"The sun rising over the green plains of Rohan",
"Rows of military tents and wooden barracks",
"Three heroic Rohirrim commanders standing together",
"A herd of wild horses running across the plains",
"A spear tip pointing at a discarded orc helmet",
"A wooden watchtower overlooking a valley",
"A large crowd of Rohirrim soldiers cheering with spears raised",
"Hands breaking iron chains against a sky background",
"Three hands joining together in a pact",
"A signal fire burning brightly on a mountain peak",
"A massive cavalry charge with spears leveled, screaming warriors",
"The White Tree of Gondor and the White Horse of Rohan side by side",
"Two kings in armor shaking hands on a battlefield",
"A leaf, a white hand, and a horse symbol arranged in a triangle",
"A sword pointing forward aggressively",
"The face of an Ent peering from a forest",
"A glowing elven phial held in a hand",
"A giant eagle flying against the sun",
"A white wizard staff glowing with light",
"A magical orb glowing with swirling lights",
"A map of Middle Earth with Rohan, Isengard, and Lothlorien highlighted",
"An executioner's axe resting on a wooden block",
"A wizard standing outside a closed heavy door in the rain",
"White Simbelmyne flowers growing on a burial mound",
"A crown suspended by marionette strings",
"A dark storm cloud casting a shadow over the Golden Hall",
"A golden crown resting on a velvet cushion",
"A queen sitting on a throne with a dark shadow looming behind her",
"Two wedding rings resting on a royal decree",
"A royal family tree scroll with names crossed out",
"An iron gauntlet slamming down on a table",
"A figure kneeling before a banner of the White Hand",
"A contract being signed with a quill",
"A half-orc enforcer standing with arms crossed",
"A massive wall of black stone and iron",
"Two mysterious diplomats in long robes conversing",
"A white staff being broken in two",
"A lone rider holding a flag riding into the sunset",
"A dagger stabbed into a map of neighboring lands",
"A warhorse rearing up triumphantly",
"The Great Eye of Sauron visible within a crystal ball",
"Several dark banners flying together under a red sky",
"A hand tightly gripping a scepter",
"A golden eagle standard shining with rays of light",
"A royal guard standing at attention in polished armor",
"Many eyes watching from the shadows",
"Five distinctive banners representing the regions of Rohan",
"A map highlighting the western region of Rohan",
"A stern commander pointing a baton",
"A rough wooden shield and axe of Dunland style",
"A red shield with a white horn symbol",
"Two regional maps being stitched together",
"Wooden scaffolding around a stone tower",
"A map highlighting the central-western plains of Rohan",
"An empty commander's chair with a sword leaning against it",
"Smoke rising from small industrial workshops in a valley",
"A marshal's baton resting on a map of the Westemnet",
"A wagon of supplies being handed over to Uruk-hai",
"A map highlighting the northern grassy plains of Rohan",
"A line of supply wagons stretching to the horizon",
"A golden sheaf of wheat tied with a ribbon",
"Elven lembas bread wrapped in a mallorn leaf",
"Workers laying stones for a new road",
"A map highlighting the eastern plains of Rohan",
"A mine cart full of ore coming out of a tunnel",
"A ledger book and a stack of coins",
"The stone foundation of a new building being laid",
"A map highlighting the southeastern region of Rohan",
"A weaving loom with green fabric",
"A wooden rack filled with freshly made spears",
"A wooden palisade fence along a river bank",
"A crowded great hall with many banners hanging from the ceiling",
"Blocks of soldiers in formation viewed from above",
"A rider blowing a war horn on a hill",
"A bundle of arrows tied together with a rope",
"A town crier reading a scroll to a crowd",
"A heavy boot stepping on a pamphlet",
"A crown resting on top of a crossed sword and shield",
"A heavy iron vault door with the Rohan crest",
"A hand scattering coins like seeds across a map",
"A single large stack of gold coins on a map",
"A loaf of bread and a rationing card",
"A quill pen writing on parchment",
"A rustic barn and a windmill in a field",
"An iron plow sitting in a furrowed field",
"A tall wooden grain silo filled to the brim",
"A row of timber-framed houses along a cobbled street",
"A map with red lines connecting towns",
"Colorful market stalls filled with goods",
"A cluster of thatched roof huts with smoke rising",
"Cavalry riding in a wedge formation",
"A warhorse wearing heavy chainmail barding",
"A heavy lance shattering a shield",
"A light horse galloping at full speed, blurred background",
"A rider drawing a bow while on horseback",
"A highly decorated Rohirrim helmet with a horse plume",
"A mare and a foal grazing in a paddock",
"Hundreds of riders charging with the sun behind them",
"A medieval wooden treadwheel crane lifting stone",
"A neat stack of white limestone bricks",
"A traditional wooden smock mill against a blue sky",
"Masons laying heavy stone blocks for a wall",
"The wooden frame of a house being raised",
"A catapult loaded with a stone ready to fire",
"A white stone wall built in the style of Gondor",
"A crude, spiked siege tower made of dark iron and wood",
"A large trebuchet with a counterweight",
"A room filled with scrolls and tapestries",
"A stone chisel and a smith's hammer crossed",
"Glass flasks filled with colorful liquids",
"A scholar in foreign robes holding a map",
"The black tower of Orthanc with scaffolding around the base",
"Two hands shaking over a snowy mountain range",
"The black stone chair of the Steward of Gondor",
"The winged crown of Gondor resting on a sword",
"A silver swan symbol and a white horse symbol intertwined",
"A shield-maiden's shield resting next to a white tree banner",
"A small boat crossing a wide river",
"A golden goblet filled with red wine",
"A bell tower with a mountain in the background",
"A caravan of trade wagons crossing a bridge"
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