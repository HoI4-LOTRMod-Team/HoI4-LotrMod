from pathlib import Path
import sys
import datetime
import subprocess
import re

from pdx_parser import *
from locfile import *

# CONFIGURATION

BASE_PATH = Path(__file__).parent.parent.parent.resolve()
ideas_file = BASE_PATH / r'common\ideas\TEMP.txt'
country_leader_traits_file = BASE_PATH / r'common\country_leader\00_traits_lotr_TEMP.txt'
army_leader_traits_file = BASE_PATH / r'common\unit_leader\00_traits_lotr_TEMP.txt'
characters_file = BASE_PATH / r'common\characters\TEMP.txt'
scripted_effects_file = BASE_PATH / r'common\scripted_effects\temp_scripted_effects.txt'
scripted_triggers_file = BASE_PATH / r'common\scripted_triggers\temp_scripted_triggers.txt'

events_file = BASE_PATH / r'events\Temp.txt'

lotr_locs_file = BASE_PATH / r'localisation\english\0_lotr_core\lotr_misc_l_english.yml'

new_idea_template = """
        $TOKEN_NAME$ = {
            allowed = { always = no }
            allowed_civil_war = { always = yes }
            removal_cost = -1

            picture = grima_wormtongue_corruption # TODO

            modifier = {
                # TODO
            }
        }
"""

new_hidden_idea_template = """
        $TOKEN_NAME$ = {
            modifier = {
                # TODO
            }
        }
"""

new_leader_trait_template = """
    $TOKEN_NAME$ = {
        random = no

        stability_factor = 0.1 # TODO
    }
"""

new_unit_leader_trait_template = """
    $TOKEN_NAME$ = {
        type = land
		trait_type = personality_trait

        new_commander_weight = {
            factor=0
        }

		planning_skill = 1 # TODO
    }
"""

new_scripted_effect_template = """
$TOKEN_NAME$ = {
    # TODO
}
"""

new_scripted_trigger_template = """
$TOKEN_NAME$ = {
    # TODO
    always = no
}
"""

new_character_template = """
	$TOKEN_NAME$ = {
		name="$TOKEN_NAME$" # TODO
		portraits={
			army={
				large="GFX_portrait_spiders_generic_2" # TODO
				small = "GFX_idea_portrait_spiders_generic_2"
			}
		}
		# TODO
	}
"""

new_event_template = """
# $TOKEN_COMMENT$
country_event = {
	id = $TOKEN_ID$.$TOKEN_NUM$
	title = $TOKEN_ID$.$TOKEN_NUM$.t
	desc = $TOKEN_ID$.$TOKEN_NUM$.d
	picture = GFX_report_event_elven_alliance # TODO

	is_triggered_only = yes

	option = {
		name = $TOKEN_ID$.$TOKEN_NUM$.a
		ai_chance = {
			base = 1
		}
	}
}
"""


def add_idea(name):
    ideas = ParseListFromFile_asPObj(ideas_file)
    new_idea_txt = new_idea_template.replace("$TOKEN_NAME$", name)
    ideas.Get("ideas").Get("country").Insert(new_idea_txt)
    SaveObjValueToFile(ideas, ideas_file)

def add_hidden_idea(name):
    ideas = ParseListFromFile_asPObj(ideas_file)
    new_idea_txt = new_hidden_idea_template.replace("$TOKEN_NAME$", name)
    ideas.Get("ideas").Get("hidden_ideas").Insert(new_idea_txt)
    SaveObjValueToFile(ideas, ideas_file)

def add_new_country_leader_trait(name):
    traits = ParseListFromFile_asPObj(country_leader_traits_file)
    new_trait_txt = new_leader_trait_template.replace("$TOKEN_NAME$", name)
    traits.Get("leader_traits").Insert(new_trait_txt)
    SaveObjValueToFile(traits, country_leader_traits_file)

def add_new_unit_leader_trait(name):
    traits = ParseListFromFile_asPObj(army_leader_traits_file)
    new_trait_txt = new_leader_trait_template.replace("$TOKEN_NAME$", name)
    traits.Get("leader_traits").Insert(new_trait_txt)
    SaveObjValueToFile(traits, army_leader_traits_file)

def add_new_scripted_effect(name):
    with open(scripted_effects_file, "a") as f:
        screff = new_scripted_effect_template.replace("$TOKEN_NAME$", name)
        f.write("\n\n"+screff)

def add_new_scripted_trigger(name):
    with open(scripted_triggers_file, "a") as f:
        screff = new_scripted_trigger_template.replace("$TOKEN_NAME$", name)
        f.write("\n\n"+screff)

def add_new_character(name):
    chars = ParseListFromFile_asPObj(characters_file)
    new_char_text = new_character_template.replace("$TOKEN_NAME$", name)
    chars.Get("characters").Insert(new_char_text)

    SaveObjValueToFile(chars, characters_file)


def add_new_event(name):
    events = ParseListFromFile_asPObj(events_file)
    namespace = events.Get("add_namespace").value
    max_id = -1
    evs = events.GetAll("country_event").value
    for obj in evs:
        raw = obj.GetVal("id")
        number = int(raw.split(".")[-1])  
        if number > max_id:
            max_id = number
    if max_id < 0: max_id = 1
    else: max_id += 1
    event_text = new_event_template.replace("$TOKEN_COMMENT$", name).replace("$TOKEN_NUM$", str(max_id)).replace("$TOKEN_ID$", namespace)
    events.Insert(event_text)
    SaveObjValueToFile(events, events_file)
    subprocess.run("clip", text=True, input=namespace+"."+str(max_id))


def process_location(loc):
    s = loc  # Ensure you define 's' or just use 'loc' throughout
    if len(s) >= 2:
        # Check if it starts/ends with quotes and strip them
        if s[0] == '"' and (len(s) == 1 or s[1] != '\\'):
            s = s[1:]
        if s[-1] == '"' and len(s) >= 2 and s[-2] != '\\':
            s = s[:-1]
    return s

def copy2clip(txt):
    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, text=True)
    process.communicate(input=txt.strip())

def extract_localization(name, loc):
    print(name)
    print(loc)
    locf = LocFile(lotr_locs_file)
    loc = process_location(loc)
    locf.add(name, loc)
    locf.save(lotr_locs_file)
    copy2clip(name)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a command (add, clear, count)")
        sys.exit(1)

    command = sys.argv[1]
    args = " ".join(sys.argv[2:])

    if command == "idea":
        add_idea(args)
    elif command == "hidden_idea":
        add_hidden_idea(args)
    elif command == "country_leader_trait":
        add_new_country_leader_trait(args)
    elif command == "unit_leader_trait":
        add_new_unit_leader_trait(args)
    elif command == "scripted_effect":
        add_new_scripted_effect(args)
    elif command == "scripted_trigger":
        add_new_scripted_trigger(args)
    elif command == "character":
        add_new_character(args)
    elif command == "event":
        add_new_event(args)
    elif command == "localization":
        extract_localization(sys.argv[2], " ".join(sys.argv[3:]))
    else:
        print(f"Unknown command: {command}")