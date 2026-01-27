

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

random_insert = """This icon is for the Spiders of Mirkwood, so stick to a red and black, aggressive theme."""

random_chance = 0.5

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


prompt_list = [
    "A close up of spider mandibles dripping with green venom, dark background",
    "A large spider eating a smaller spider, dark silhouette style",
    "Multiple white spider egg sacks hanging from a dark branch",
    "A swarm of hundreds of tiny black spiders crawling over a rock",
    "A single large pulsating spider egg sac glowing with a faint green light",
    "A feast table covered in thick cobwebs with bones scattered on top",
    "Dark burrows and holes at the base of a twisted tree covered in webbing",
    "Many pairs of red glowing spider eyes staring out from the darkness of a forest",
    "A massive complex web structure spanning between giant dark trees",
    "A massive heavily armored spider standing guard in front of a cave entrance",
    "Dark twisted vines and webs strangling a green tree",
    "A thick layered spider web forming the shape of a shield",
    "Sharp spider fangs dripping with venom ready to strike",
    "A hairy spider leg stepping out of shadow into a sunlit grassy field",
    "A spider wearing a jagged iron crown sitting atop a high web",
    "A large spider pressing a smaller submitting spider into the dirt",
    "A spider silhouette bowing before the flaming Eye of Sauron",
    "A broken elven bow entangled in spider webs",
    "A dwarven helmet cracked open with webs inside",
    "A rotting orc skull with a spider crawling out of the eye socket",
    "A ray of white light illuminating a complex spider web design",
    "A terrifyingly large ancient spider descending from a rocky crevice",
    "A spider casting a shadow that looks like a primordial dark monster",
    "A map of a forest completely covered in a layer of grey webbing",
    "A boot stepping into a hidden tripwire made of spider silk",
    "Thick webs stretched between high tree tops catching falling debris",
    "A spider standing triumphantly on top of a pile of rocks",
    "Spiders gathered in a circle around a carcass in a dark clearing",
    "Several spiders in a circle with faint purple psychic waves connecting them",
    "A lean agile spider leaping forward with blurred motion",
    "An infinite loop symbol made of spider silk",
    "Multiple spider legs skillfully weaving a complex intricate pattern",
    "A spider web glistening with dew that looks like glowing magical orbs",
    "Rows of spiders marching in perfect unison like soldiers",
    "A large mother spider sheltering many tiny spiders under her legs",
    "A diagram of spider anatomy drawn on parchment",
    "Three large spiders sitting on raised rock thrones facing a crowd",
    "A close up of a spider's face screeching in fury with red aura",
    "Green pheromone mist floating calmly through a dark forest",
    "A single large authoritative eye looking down from a high web",
    "A spider warrior with chitin plates glowing with inner power",
    "Spiders using silk to pull two large stones together",
    "Multiple black arrows pointing outward from a central nest on a map",
    "Dark webs wrapping around a glowing lantern and snuffing out the light",
    "A wall made of grey stone reinforced with thick layers of white web",
    "A strange workshop building constructed entirely from hardened silk",
    "A cross-section view of tunnels and chambers deep underground",
    "Spiders digging into the earth expanding a tunnel",
    "A deep dark pit with spiral webbing going down into the abyss",
    "A thick thread of silk connecting a dark tree to a stone tower",
    "A commander spider gesturing with a leg towards the horizon",
    "A massive tide of black spiders flooding over a hill",
    "A view from a dark forest looking out at distant mountains and plains",
    "A globe of Middle-earth partially covered in a spider web",
    "A spider examining a glowing magical artifact with its pedipalps",
    "A close up of jagged spider fangs glistening with venom",
    "A venom gland spraying a stream of green liquid",
    "A perfectly geometric spider web blueprint on a dark surface",
    "A spider sensing vibrations on a single thread of silk in the dark",
    "A shadowy predator silhouette stalking prey through tall grass",
    "Green acid melting through a metal plate",
    "Gears and mechanical parts held together by sticky spider silk",
    "Glowing purple magical runes woven into a spider web",
    "All threads of a web converging on a single glowing point of light",
    "A magnifying lens focusing light onto a spider fang",
    "A spider watching a human settlement from a high tree branch",
    "A spider with sparks of electricity or magic around its head",
    "A stylized image of a spider evolving into a more perfect form",
    "Small spiders consuming the carcass of a massive dead spider",
    "A spider spinning a web in the void unconnected to anything else",
    "A blue river winding through a landscape with a spider shadow over it",
    "Spider eggs safely nestled behind a heavy iron grate or stone wall",
    "Glowing crystals and ores embedded in the walls of a spider cave",
    "A dark pit lined with sharp wooden spikes and spider fangs",
    "A pulsing brain-like structure located in the center of a web nest",
    "Webs stretching out to cover factories and buildings",
    "A spider mutating with uneven limbs and strange growths",
    "A perfectly symmetrical spider diagram with ruler measurements",
    "A black iron chest with the symbol of Mordor being opened by spider legs",
    "Spiders carrying wrapped bundles of silk towards a dark tower in the distance",
    "A boundary stone in the forest marked with both spider and elven runes",
    "A spider passing a scroll to an elven hand",
    "A gruesome offering of raw meat placed on a flat stone",
    "A spider resting on the branch of a large walking tree ent",
    "A view from the forest looking out towards the setting sun in the west",
    "Two dark shadowy hands clasping together in agreement",
    "Many different colored threads being woven together into a single strong rope",
    "A spider with its mandibles bound by a silver chain",
    "A pile of discarded chitin carapaces and sharpened fangs ready for use",
    "A spider watching a battle from a high vantage point and taking notes",
    "A dwarf beard and helmet lying in a pool of blood",
    "A delicate elven circlet lying broken on the forest floor",
    "A black tower completely covered in thick white spider webs",
    "A crude goblet filled with fresh red blood",
    "An empty larder with only a few cobwebs inside",
    "Spiders emerging from egg sacks with aggressive postures",
    "A crude map painted on bark with a red arrow pointing upwards/North",
    "Spiders crawling back towards a central dark cave entrance",
    "A crude map painted on bark with a red arrow pointing downwards/South",
    "A northern pine forest with spider fortifications between the trees",
    "Grey corruption spreading across a green landscape",
    "A dark southern swampy forest with spider fortifications",
    "A pile of assorted humanoid skulls cracked open",
    "A massive citadel constructed entirely of hardened spider silk and dark wood",
    "A giant spider leg slamming down onto a map of the region",
    "The One Ring gold and glowing caught in a sticky spider web",
    "A spider and an orc standing side by side looking at a common enemy",
    "A gaping maw of darkness consuming the landscape",
    "Pale elven skin marked with venomous bite marks",
    "Black viscous blood pooling on the ground",
    "Spiders posted as sentries on the perimeter of a dark forest"
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