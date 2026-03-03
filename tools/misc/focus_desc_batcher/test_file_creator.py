

import json
import copy
import random


request_template = {
    "key": "text_request_NUM",
    "request": {
        "contents": [{
            "parts": [
                {"text": "PROMPT"},
                {
                    "file_data": {
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/hzvw9d5edpo8", 
                        "mime_type": "text/plain"
                    }
                },
            ]
        }],
        "generationConfig": {
            "responseModalities": [ "TEXT" ],
        }
    }
}

prompt_template = """
I am working on a HoI4 mod that takes place in the LOTR universe. 

I'm currently working on a focus tree for the Easterlings of Rhûn.
The implementation is complete and ready, but I need your help in writing some flavor-descriptions for the focuses.

I've attached the entire file of the focus tree so that you can deduce the focus tree structure and the general paths and effects. Some parts are still work-in-progress.


Here are some example descriptions that I like, which you can use as a style guide:

lth_acknowledgethemordorthreat_desc:0 "A shadow stirs in the east. It's threat is spreading along the misty mountains and engulfing our peaceful enclave. The looming storm can no longer be denied, and requires a radical rethinking of our present imperatives."
lth_thegreatschism_desc:0 "Lord Celeborn and Lady Galadriel have blessed Lothlórien with their joint, benevolent rule for many centuries. Only broken hearts could lead them down a darker path."
ROH_attract_foreign_scholars_desc:0 "The libraries of Edoras may pale in comparison to those in Minas Tirith, but we may enlist the help of foreign scholars to help us catch up."
ROH_purge_grima_sympathizers_desc:0 "Our court is infested with disloyalists and traitors. We must cleanse the realm of their influence and restore honor to Rohan."
ROH_deny_gandalf_entrance_desc:0 "Does this old man think us fools? We have suffered enough treachery at the hand of wizards to fall for his tricks!"
ROH_the_shadow_over_rohan_desc:0 "Farewell to the old, feeble Rohan, chasing idealism and dreams. The time has come for a new order."
ROH_dynastic_legitimacy_desc:0 "This monarchy is absolutelry, definitely, 100% legit."
ELU_old_kingdom_not_forgotten_desc:0 "The ancient lines of the Seven Fathers that go back to the days of Durin the Deathless are now little more than tales and legends. Tales we have not forgotten."
ELU_dwarven_supremacy_desc:0 "The rock and stone, it calls to us. Do you feel it? It is the destiny of the mountain, to stand over the plains and forests."
elu_operationglimmerpeakassault_desc:0 "'Wait, what's that? Is that a dwar-- AUUGH!', said the elf before his helmet was caved in by a hammer."

As you can see, the descriptions are typically not longer than a few sentences and provide a flavorful description of each focuses' actions/effects, causes or context. On some occasions they may even stray into some mild humor or irony.

I want you to provide me with 5 different potential descriptions only for the following focus: PROMPT

Provide me the descriptions in the following format:

focus_name_desc:0 "focus description 1"
focus_name_desc:0 "focus description 2"
focus_name_desc:0 "focus description 3"
focus_name_desc:0 "focus description 4"
focus_name_desc:0 "focus description 5"

Provide only this list of descriptions and no other text at all.
"""

prompt_list = [
"RGL_a_people_under_threat",
"RGL_the_politics_of_survival",
"RGL_seek_a_protector",
"RGL_stand_alone",
"RGL_seek_guarantees",
"RGL_seek_an_alliance",
"RGL_seek_vassalage",
"RGL_the_shroud_of_dol_guldur",
"RGL_protection_of_the_golden_wood",
"RGL_the_elven_kings_shield",
"RGL_the_gladden_chiefs",
"RGL_emergency_defense",
"RGL_the_emergency_fyrd",
"RGL_galadhrim_marchwardens",
"RGL_invite_radagast",
"RGL_orcish_lieutenants",
"RGL_shared_army_exercises",
"RGL_let_the_wizard_lead",
"RGL_stability_through_safety",
"RGL_provoke_an_attack",
"RGL_economic_improvements",
"RGL_diplomatic_outreach",
"RGL_defensive_paranoia",
"RGL_fortification_focus",
"RGL_armed_resistance_focus",
"RGL_build_a_forge",
"RGL_provide_tribute",
"RGL_brace_for_war",
"RGL_defensive_measures",
"RGL_military_production",
"RGL_expand_the_workshops",
"RGL_vigil_of_the_woods",
"RGL_expand_woodside_villages",
"RGL_charcoal_production",
"RGL_set_up_additional_lumberyards",
"RGL_protect_administrative_centers",
"RGL_refugee_levies",
"RGL_conceal_production",
"RGL_freedom_fighters",
"RGL_the_great_wall",
"RGL_convert_farming_equipment",
"RGL_desperate_defense",
"RGL_increase_taxes",
"RGL_emergency_powers",
"RGL_try_to_barter_with_the_spiders",
"RGL_tend_to_the_woods",
"RGL_study_mirkwood_fauna",
"RGL_rhosgobel_rabbits",
"RGL_grow_bolder",
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