

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
- Use **bold primary forms** to define the shape.
- Prioritize the "feel" of the texture over microscopic details that would disappear when shrunk.
- Avoid excessive detail that would clutter the small icon.
- Use a realistic style that matches the medieval Lord of the Rings movie aesthetic.

**Background:** Render the object on a neutral, solid, flat background, as they are only elements/components.

**Subject to generate:** PROMPT
"""


prompt_list = [
"A terrifying close-up of a spider's maw dripping with green venom, representing hunger",
"A large black spider cannibalizing a smaller spider in a dark nest",
"A clutch of translucent spider eggs pulsating with life amidst bones",
"A swarm of small spider hatchlings erupting from the earth",
"Large spider eggs glowing faintly in the dark, suspended in thick webs",
"A gruesome pile of bones and skulls wrapped in silk, being feasted upon",
"Dark holes in the forest floor covered in thick webbing, representing brood lairs",
"Hundreds of glowing spider eyes peering out from the darkness of a cave",
"A massive, terrifying structure made of thick white webs and dark twisted trees, a landmark nest",
"A heavily armored giant spider standing guard over a precious egg sac",
"The trees of Mirkwood being overtaken and choked by thick grey spider webs",
"A spider rearing back with front legs raised in a defensive posture, shield symbol in background",
"A spider lunging forward with fangs bared, sword symbol in background",
"A shadowy spider silhouette stepping out of a dark cave into the light",
"A pyramid structure composed of spiders, with a massive matriarch at the apex",
"A large spider pinning down a smaller distinct spider breed, asserting dominance",
"The flaming Eye of Sauron gazing down approvingly upon a spider",
"An Elven helmet crushed and entangled in thick spider silk",
"A Dwarven axe broken in half and wrapped in spider web",
"An Orc skull dripping with green venom, impaled on a spike",
"A spider leg gently touching a glowing Elven leaf, representing a strange alliance",
"A colossal ancient spider descending from a cliff, emanating a terrified shadow",
"A shadowy silhouette of a primordial spider consuming a light source",
"A map of the Mirkwood forest completely covered in a network of white webs",
"Soldiers caught in invisible tripwires and silk traps in a dense forest",
"Thick webs stretching between tree tops catching a falling airplane or eagle",
"A spider rising above others on a pedestal of silk, glowing with power",
"A ritualistic circle formed by spider legs and bones",
"Multiple spiders with glowing minds connecting via a psychic web link",
"A scarred, muscular spider with sharp mandibles and a warrior aesthetic",
"An ouroboros symbol made of a spider eating its own tail, representing endless struggle",
"Three wise spiders weaving a complex tapestry of fate together",
"A spider with mystical glowing patterns on its back, ethereal and dreamlike",
"Geometric patterns formed by spider webs, representing order and discipline",
"An old, wise-looking spider nesting in a hollow tree, advising the brood",
"An anatomical drawing of a spider in a vintage scientific style",
"Several spiders gathered around a central matriarch in a court setting",
"Red glowing spider eyes filled with rage and fury",
"Green pheromone clouds soothing a group of agitated spiders",
"A crude crown resting on a spider's head, representing centralized will",
"Spider legs mutating into jagged metal blades or armored spikes",
"Spiders building a complex architectural structure using silk as scaffolding",
"Spiders spreading out in all directions on a map, roaming free",
"A spider extinguishing a lantern or torch, embracing the darkness",
"A defensive wall made of thick, hardened web and stone",
"Spiders operating a primitive loom or industrial machinery made of wood and silk",
"A cross-section of the earth showing deep tunnels filled with spiders",
"More tunnels being dug deep into the earth by worker spiders",
"A deep, vertical pit lined with silk descending into the abyss",
"Two different species shaking hands, but one hand is a chitinous spider leg",
"A pack of spiders hunting a deer in perfect coordination",
"An ocean of small spiders covering the ground completely",
"A spider looking greedily at a map of the Anduin river valley",
"A globe of the world wrapped entirely in spider webs",
"A spider examining a scroll or book, seeking knowledge",
"A close-up of dripping, razor-sharp spider fangs",
"A spider shooting a jet of venom like a projectile weapon",
"Geometric web structures showing structurally sound engineering",
"Vibrations moving along a single thread of web, representing spying",
"A spider camouflaged perfectly against tree bark, waiting to strike",
"Acid melting through a metal shield, corrosive force",
"A machine or contraption held together by strong silk ropes instead of bolts",
"Purple magical energy emanating from a spider's abdomen",
"A brain made of glowing web connections, representing converged wisdom",
"A magnifying glass focusing light on a single point, representing focused research",
"Spiders observing humans from the shadows, stealing secrets",
"Spiders with glowing eyes looking up at the stars, visionary",
"A DNA helix made of spider silk, mastery of biology",
"A swarm of small spiders consuming the body of a matriarch",
"A solitary spider spinning a complex isolated web, refusing allies",
"A spider planning a route on a tactical map (generic planning focus)",
"A mysterious spider ritual in the dark (generic mystery focus)",
"A river flowing into a dark gaping spider mouth",
"Armored egg sacs protected by stone walls and bunkers",
"Spiders mining glowing crystals or mushrooms in a deep cave",
"Pits in the ground filled with spikes and venom",
"A spider head glowing with increased intelligence and cunning",
"The forest floor expanding outward, covered in creeping web",
"A chaotic spiral of web spinning out of control, erratic mutation",
"A spider leg growing larger and stronger in three visible stages",
"Black iron armor pieces and weapons being gifted to a spider",
"Cocoons containing victims being offered to a dark tower in the distance",
"A border line drawn in the forest, respected by both spiders and elves",
"An Elf and a Spider exchanging scrolls or knowledge",
"A handshake between a spider leg and a hand, dripping with blood (Non-Aggression Pact)",
"A spider resting on the branch of a living walking tree (Ent)",
"A signal fire lit on a hill, seen through a spider web",
"Shadows of a spider and a Nazgul wraith merging together",
"Multiple webs connecting different strongholds on a map, a great weave",
"A muzzle made of silk placed on a spider, restraining hunger",
"Piles of detached sharp spider legs and carapaces for use as weapons",
"A spider changing color to match its environment, adaptive camouflage",
"Dwarf helmets scattered in a spider larder, being devoured",
"Elven bows broken and covered in web, feasting on the fair",
"Black Orc armor tangled in white webs, eating the rotten",
"A chalice filled with blood held by a spider leg, warm blood",
"Empty larders and skeletal spiders, representing economic hunger",
"Thousands of spiders marching in military formation",
"A compass arrow pointing North, covered in web",
"Spiders retreating and returning to a central hole",
"A compass arrow pointing South, covered in web",
"A northern fortress covered in webs",
"Black creep spreading across a green map, endless sprawl",
"A southern outpost covered in webs",
"A generic icon of a spider gazing into the future (placeholder)",
"A generic icon of a spider weaving a complex plan (placeholder)",
"A generic icon of a spider brooding in the dark (placeholder)",
"Humanoid footprints being erased by thick spider webs",
"A massive tower of web rising above the tree line",
"A spider asserting control over a region, gripping it tightly",
"The One Ring caught in a spider web, glinting gold",
"A Spider, an Orc, and a Man standing together, putting differences aside",
"A black hole shaped like a mouth consuming the world, Ungoliant's appetite",
"Soft meat hanging in a larder, tender flesh",
"Black blood spattered on a white web",
"Spiders patrolling a perimeter fence made of silk"
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