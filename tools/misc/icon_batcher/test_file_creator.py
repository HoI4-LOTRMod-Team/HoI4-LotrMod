

import json
import copy


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



prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. 
I've attached some example images as a style guide, which would correspond to the following prompts:
"A trio of medieval soldiers with leather armor and swords",
"A red medieval flag waving in the wind",
"Faramir and Eowyn from LOTR holding hands while getting wed".

**Artistic Style (Reference Examples):**
Follow the painterly, hand-illustrated style of these examples. Use muted, grounded colors, realistic textures (metal, cloth, wood), and soft cinematic lighting. Avoid flat colors, thick black outlines, and the "mobile-game cartoon" look.

**Readability & Scale:**
The final icon will be displayed at a small size (200x200). To ensure clarity at this scale:
- Focus on a **strong, recognizable silhouette**.
- Use **bold primary forms** and high-contrast lighting to define the shape.
- Prioritize the "feel" of the texture over microscopic details that would disappear when shrunk.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Subject to generate:** PROMPT
"""


prompt_list = [
"A stylized map of the Blue Mountains with a question mark hovering over the peaks",
"A snow-capped mountain peak with a glowing dwarven rune carved into the rock face",
"A dusty, ancient dwarven crown resting on a stone pedestal, illuminated by a shaft of light",
"A rolled parchment scroll with a heavy royal wax seal being held out by a hand",
"A dwarf lord kneeling to receive a crown, bathed in golden light",
"A round stone table with several empty stone chairs around it",
"A marshal's baton resting on a tactical map of the mountains",
"A heavy fist clenching several small figurines or tokens",
"A pickaxe raised high in a fist, stylized in a revolutionary poster art style",
"A minecart overflowing with raw iron ore",
"Green hemp plants growing in a rocky planter or field",
"A handshake between a dwarf and a merchant with a gear symbol in the background",
"Two crossed pickaxes in front of a shield",
"A flag being planted firmly on top of a mine entrance",
"A document stamped with a pickaxe symbol",
"A compass held in a hand, with the needle pointing sharply towards a sword",
"A heavy iron boot stepping on a burning pamphlet",
"A wooden sign reading 'Union' being snapped in half",
"A silhouette of a king walking away into a blizzard, head down",
"An iron dwarven gauntlet crushing a delicate elven ornament",
"A dwarf king in full plate armor holding a battleaxe",
"A dwarf king wearing robes holding a quill and scroll",
"A sword linking two broken chain links together",
# "A map of Eriador with the edges burning",
# "An axe cutting into a stylized white tree",
# "A steam train or minecart on tracks carrying crates of supplies",
# "A red tactical arrow pointing at a mountain peak",
# "A blacksmith hammering out a dent in a breastplate",
# "A dwarf in heavy armor riding a large mountain goat charging forward",
# "A shield wall of dwarves standing firm amidst swirling snow",
# "Veterans with long grey beards holding weapons, standing in formation",
# "A dagger plunged into a map of human lands",
# "A dwarf handing a bag of gold to a shadowy, hunched goblin figure",
# "A dwarf and an elf shaking hands, though the atmosphere looks tense",
# "A shadowy figure whispering into the ear of a man",
# "A hobbit hole with black smoke rising from the chimney, suggesting unrest",
# "A broken crown of Arthedain lying in the mud",
# "A market stall collapsing, with coins spilling onto the ground",
# "A red arrow piercing a burial mound",
# "An iron helmet surrounded by storm clouds and lightning",
# "An ancient book of grudges open to a specific page",
# "A cornucopia overflowing with gold coins and gemstones",
# "A shield with a fortress icon painted on the front",
# "A wagon load of vegetables and barrels of food",
# "A pile of animal furs being exchanged for metal tools",
# "A white dove carrying a scroll flying towards a tall white tower",
# "A cogwheel made half of dwarven iron and half of elven silver",
# "A sword being slid into a scabbard",
# "Two shields leaning against each other, one dwarven style, one elven style",
# "A dwarven mason repairing a human stone wall",
# "A thriving market stall with piles of goods and happy traders",
# "A wooden longship sailing on blue water",
# "Crates stamped with dwarven runes being unloaded from a wagon",
# "A convoy of wagons traveling towards a white city in the distance",
# "The White Tree of Gondor protected by a dwarven shield",
# "A group of dwarven soldiers waving goodbye as they march out",
# "A sickle and a hammer crossed over a sheaf of wheat",
# "A bag of gold placed on a map of a river valley",
# "A wooden farmhouse on wheels being moved",
# "A fishing net pulled from the water full of fish",
# "Gold coins raining down on a field of crops",
# "A mortar and pestle with green herbs",
# "A chalkboard with tactical drawings and arrows",
# "A tight phalanx formation of dwarven shields",
# "A boot with crampons climbing a steep rock face",
# "A sniper or scout in white camouflage hiding in snowy rocks",
# "Soldiers training with wooden practice weapons",
# "A complex battle plan on a map with dwarven runes",
# "A military medal or badge of honor with crossed swords",
# "A factory smokestack puffing smoke into the cold air",
# "A glowing anvil with a hammer striking it, sparks flying",
# "Construction scaffolding around a building in a valley",
# "A circular saw blade and a pile of lumber",
# "A snowy quarry with cranes and stone blocks",
# "Molten metal pouring into a cast mold",
# "A furnace roaring with intense orange fire",
# "A rack of newly forged swords",
# "A heavy breastplate displayed on a stand",
# "Rows of anvils in a large smithing hall",
# "A paved road winding through a green valley",
# "A paved road cutting through snow and ice",
# "A paved road passing through a dense forest",
# "A mine entrance reinforced with new wooden beams",
# "A pile of logs and a large woodcutter's axe",
# "A gleaming, silvery metal vein visible in dark rock",
# "A magnifying glass hovering over an ancient rune",
# "Tall bookshelves filled with stone tablets and scrolls",
# "A dusty, leather-bound tome being opened",
# "A scientist examining a glowing crystal",
# "Bubbling flasks and glass retorts on an alchemy table",
# "A glowing magical stone emitting radiation-like waves",
# "A cozy dwarven living quarter carved into stone with a fireplace",
# "Anti-air guns pointing up from a mountain peak",
# "A heavily fortified citadel gate",
# "A large drill machine or dwarves digging a tunnel",
# "A seismograph needle scribbling wildly on paper",
# "Concrete barriers and sandbags stacked for defense",
# "A line of concrete bunkers stretching across a landscape",
# "A city surrounded by thick stone walls",
# "A coastal bunker overlooking the ocean"
]

requests_list = [

]


i = 1
for prompt in prompt_list:
    p = prompt_template.replace("PROMPT", prompt)
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