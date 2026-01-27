

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/j0kl7qzfax5x", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/u6sf98te3f9r", 
                        "mime_type": "image/png"
                    }
                },
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/edi9b55ah14s", 
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

random_insert = """This icon is for the Elves of Mirkwood, so stick to greenish colors and forest themes."""

random_chance = 0.5

prompt_template = """Act as a professional concept artist creating elements for icons for a LOTR-style strategy game. 
I've attached some example images as a style guide, which would correspond to the following prompts:
"A trio of medieval soldiers with leather armor and swords",
"A red medieval flag waving in the wind",
"Faramir and Eowyn from LOTR holding hands while getting wed".

**Artistic Style (Reference Examples):**
Follow the realistic style of these examples. Avoid flat colors, black outlines, and cartoon aesthetics.
$RANDOM$

**Readability & Scale:**
The final icon will be displayed at a small size (200x200). To ensure clarity at this scale:
- Focus on a **strong, recognizable silhouette**.
- Use **bold primary forms** to define the shape.
- Prioritize the "feel" of the texture over microscopic details that would disappear when shrunk.
- Avoid excessive detail that would clutter the small icon.
- Use a realistic style that matches the medieval Lord of the Rings movie aesthetic.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Subject to generate:** PROMPT
"""


prompt_list = [
    "A majestic set of heavy wooden gates set into a hillside, leading to an underground palace",
    "An intricate elven crown illuminated by a single shaft of light, surrounded by shadows",
    "An elf clasping the hand of a human in a diplomatic handshake",
    "A map of a dense forest with a compass pointing towards the unexplored edges",
    "A barrier of elven spears pointing outward against a dark purple fog",
    "Stone reinforcements and fortifications being added to natural cave pillars",
    "Glowing lanterns hanging from ancient trees illuminating a forest path",
    "An elegant elven smithing hammer striking a glowing blade",
    "A vibrant green sapling growing out of a dead stump, symbolizing restoration",
    "Smoke rising from a ventilation shaft on a rocky mountain peak",
    "Elven arrows piercing the leg of a giant spider",
    "An old overgrown stone road being cleared of vines and roots",
    "A bag of gold coins placed on a table next to a rough iron mercenary sword",
    "An elf camouflaged in foliage looking through a spyglass",
    "Barrels of wine being loaded onto a river raft for trade",
    "A pile of scrolls and books illuminated by a foreign candle",
    "Iron dungeon bars being pried open to reveal darkness inside",
    "A feast table set under the trees with wine goblets and fruits",
    "An ancient scroll bearing the seal of Oropher next to a heavy gavel",
    "A wooden platform high in a tree canopy with a lit signal fire",
    "Two different elven banners crossed together in alliance",
    "A shadowed hooded figure whispering secrets to a stoic elf",
    "A portrait of King Thranduil wearing his autumn crown looking stern and majestic",
    "A wall of elven shields locking together to block a creeping darkness",
    "A treaty document being signed by an Elf, a Man, and a Dwarf",
    "An elven sword stabbed into a map of Middle Earth",
    "A single bright lantern shining defiantly in pitch black darkness",
    "The One Ring lying on a forest floor, glowing with a sinister light",
    "A heavy wooden desk covered in ledgers and an official guild stamp",
    "Large wooden silos filled to the brim with grain and nuts",
    "A stylized mask with a finger held over the lips requesting silence",
    "Glowing elven runes floating between two pairs of hands",
    "An arrow on a map pointing towards the dark tower of Dol Guldur",
    "Legolas's bow and Tauriel's daggers crossed over a map",
    "A roasted bird on a silver platter with wine in a festive atmosphere",
    "An elf offering a sparkling gemstone to a rough dwarven hand",
    "Coins and goods being exchanged over a river trade route",
    "Cut timber logs floating down a river towards a dark, industrial sky",
    "An orc helmet being examined and dissected on a table",
    "A glass vial containing glowing green spider venom",
    "A hooded orc holding a parchment contract",
    "A map of Mirkwood being cut in half by a knife",
    "An elaborate family tree scroll with golden leaves and silver branches",
    "An open book with Sindarin script glowing on the pages",
    "An ornate military officer's badge with a 'restricted' symbol",
    "Two elves sparring with wooden practice swords",
    "An elf in heavy armor standing partially transparent or invisible",
    "A necklace of green emeralds resting in a velvet box",
    "A dwarven axe with a red 'X' painted over it",
    "A wrapped gift caught in a sticky spider web",
    "An elven shield and a dwarven shield standing side by side",
    "A hand reaching out towards a silhouette in the distance",
    "A banner displaying the White Tree of Gondor and the Horse of Rohan",
    "The White Tree of Gondor symbol on a stone shield",
    "A white horse symbol on a green field",
    "Heavy wooden gates slamming shut and being barred",
    "A portrait of Lady Galadriel holding a silver pitcher",
    "A heavy boot crushing a spider",
    "White gems shining intensely with a hand reaching to grab them",
    "Bundles of arrows being fletched and piled up for war",
    "A broom sweeping away muddy footprints from a pristine forest floor",
    "A dwarf ambassador being pointed towards the exit by a spear",
    "A tree rapidly changing color from black corruption to healthy green",
    "Elves walking away into the deep woods carrying heavy supplies",
    "A wagon train of civilians moving through a forest road",
    "Blacksmith tools and anvils packed into wooden crates",
    "A magnifying glass hovering over a spider",
    "A magnifying glass hovering over a dark fortress tower",
    "An empty village with no lights, completely abandoned",
    "A golden mallorn leaf falling into an open hand",
    "A golden cup being filled with coins",
    "Wooden spikes pointing outwards from a dense bush",
    "A blue chemistry flask and a quill on a research table",
    "An old elf reading a book that glows with magic",
    "A saw cutting through a thick log",
    "A dagger hidden inside a sleeve",
    "A basket overflowing with red berries and mushrooms",
    "Tall wooden shelves filled with ancient books",
    "An eye symbol carved subtly into a tree trunk",
    "A tall wicker structure designed for food storage",
    "A crystal glowing with starlight representing secret knowledge",
    "A workshop producing its own tools and hammers",
    "An intricately carved wooden figurine of an animal",
    "A chemistry flask with a plus sign next to it",
    "An elven flag planted on a dark, corrupted hill",
    "The heraldry of Doriath (Thingol's sigil) displayed proudly",
    "Green roots spreading over a map to claim territory",
    "A portrait of Lord Elrond looking wise and concerned",
    "A shield with a leaf design protecting a small candle flame",
    "A simple wooden bowl with a single piece of bread",
    "Thranduil sitting on his throne, bathed in light",
    "A crown sitting on top of a pile of swords",
    "Three elves from different realms conversing in a circle",
    "A letter with a wax seal stamped with a spider symbol",
    "A distress flare signal rising from the woods",
    "Three chairs arranged in a circle in a forest glade",
    "Archers from different elven realms shooting at the same target",
    "A golden ring linking different elven heraldry symbols",
    "A cage descending over the Eye of Sauron",
    "An elf turning their back on a human village",
    "Windows being boarded up and spears being sharpened",
    "A balanced weighing scale made of wood",
    "Bellows blowing air into a fire to stoke it",
    "An elf standing firm and unmoving in a violent storm",
    "Elven architects looking at blueprints for a new building",
    "A broken sword being held defiantly",
    "A dwarf and an elf looking closely at a gem together",
    "Dwarven infantry protecting elven archers in formation",
    "An elf riding a horse of Rohan",
    "An elf looking into a mirror and seeing an orc reflection",
    "An elven harp being smashed on the ground",
    "Hands clutching a glowing crystal orb to protect it",
    "Elven skin turning grey and scarred with corruption",
    "An elf and an orc standing back to back in battle",
    "A large troll smashing a rock with a club",
    "A wooden signpost pointing to two different dark paths",
    "A black iron crown with sharp spikes",
    "An elf kneeling in submission before the Eye of Sauron",
    "Crates of black iron weapons arriving from the east",
    "Scavenging armor and weapons from a battlefield",
    "Shadows lengthening across a forest floor at sunset",
    "An arrow flying towards the sunset in the west",
    "A cracked and broken dwarven helmet",
    "A throne made of living roots and vines",
    "Legolas holding a dagger behind his back, looking conflicted",
    "A shield wall facing the entrance of a spider cave",
    "Spider webs being burned away from a tree trunk",
    "A hand demanding a blue ring with a sapphire (Vilya)",
    "A hand demanding a white ring with adamant (Nenya)",
    "A magical barrier being shattered by a warhammer",
    "A giant bear and an elf standing together",
    "A mountain fortress with orc banners being besieged",
    "The coat of arms of Dale (The Archer) on a banner",
    "A boat on the Long Lake carrying trade goods",
    "A dwarf whispering secrets to an elf in the shadows",
    "A dwarven beard catching on fire",
    "A sack overflowing with gold and gems",
    "An elf dropping their banner in the mud",
    "An orc archer hiding in a tree ambush",
    "Burning buildings in a beautiful valley like Rivendell",
    "A golden tree (Mallorn) catching on fire",
    "A forge hidden inside a hollowed-out giant tree trunk",
    "Elves working in a cave entrance covered by camouflage bushes",
    "A magical light pushing back a purple fog",
    "A fist clenching around a map of Mirkwood",
    "Replanting saplings in a burnt area of the forest",
    "Glowing eyes visible in the dark bushes",
    "A small wooden fort built in a swampy area",
    "A tall watchtower looking out over a wasteland",
    "An elven flag flying high over the entire forest canopy",
    "A torn map being taped back together",
    "A sword slicing cleanly through a thick spider web",
    "Battering rams attacking a dark iron gate",
    "Sunlight breaking through the canopy with birds flying",
    "A wooden bridge being constructed over a river",
    "A giant bear track in the mud next to an elven boot print",
    "A rustic wooden hut with smoke coming from the chimney",
    "Complex pulley systems made of wood and rope",
    "A honeycake and a piece of lembas bread on a plate",
    "A human family walking into an elven village with luggage",
    "A portrait of Radagast the Brown with a bird's nest in his hat",
    "A water wheel covered in vines and moss",
    "Elves constructing a wooden frame for a building",
    "An anvil with leaf engravings on the side",
    "Houses built seamlessly into the sides of giant trees",
    "A mine shaft entrance reinforced with elegant woodwork",
    "A camouflaged elf aiming a bow from the brush",
    "A giant eagle soaring against the sun",
    "The massive underground gates of Thranduil's halls",
    "Sparks flying from a hammer hitting hot steel",
    "Heavy stone doors with intricate elven carvings",
    "A sharp curved elven sword gleaming",
    "Rows of weapon racks filled with spears",
    "A large bird nest on a cliff edge containing eggs",
    "Collecting sap from a rubber tree in a bucket",
    "Watchtowers facing a gathering dark cloud",
    "An elf speaking to a captivated audience"
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