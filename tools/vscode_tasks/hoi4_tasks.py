from pathlib import Path
import sys
import datetime

from pdx_parser import *

# CONFIGURATION

BASE_PATH = Path(__file__).parent.parent.parent.resolve()
ideas_file = BASE_PATH / r'common\ideas\spiders.txt'
country_leader_traits_file = BASE_PATH / r'common\country_leader\00_traits_lotr_spi.txt'
army_leader_traits_file = BASE_PATH / r'common\unit_leader\00_traits_lotr_spiders.txt'
characters_file = BASE_PATH / r'common\characters\SPI.txt'
history_file = BASE_PATH / r'history\countries\SPI - Spiders.txt'
scripted_effects_file = BASE_PATH / r'common\scripted_effects\spiders_scripted_effects.txt'
scripted_triggers_file = BASE_PATH / r'common\scripted_triggers\spiders_scripted_effects.txt'
tag = "SPI"


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
    
    with open(history_file, "a") as f:
        f.write("\n\nrecruit_character = "+name)

    SaveObjValueToFile(chars, characters_file)


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
    else:
        print(f"Unknown command: {command}")