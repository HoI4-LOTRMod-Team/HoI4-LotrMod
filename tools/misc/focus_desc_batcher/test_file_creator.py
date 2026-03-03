

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/mdnpubgtfop4", 
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

I'm currently working on a focus tree for the Orcs of Dol Guldur. The implementation is complete and ready, but I need your help in writing some flavor-descriptions for the focuses.

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
"DGU_rearmament_effort",
"DGU_the_shadow_over_the_mirkwood",
"DGU_instill_strict_discipline",
"DGU_encourage_individual_initiative",
"DGU_revised_army_drills",
"DGU_meritocratic_army_command",
"DGU_the_grand_strategy",
"DGU_enxtinguish_elven_light",
"DGU_burn_the_ancient_woods",
"DGU_poison_the_river_running",
"DGU_weaken_the_woodland_guard",
"DGU_a_match_for_elven_might",
"DGU_the_siege_of_the_elven_halls",
"DGU_terror_of_the_anduin",
"DGU_stalk_the_vales",
"DGU_cross_the_old_ford",
"DGU_divide_the_woodmen_clans",
"DGU_attack_rohan",
"DGU_the_armies_of_the_necromancer",
"DGU_siege_trolls",
"DGU_dark_sorcery",
"DGU_the_forges_of_night",
"DGU_war_forges",
"DGU_the_eyes_eyes",
"DGU_sorcerous_spires",
"DGU_necromantic_forge",
"DGU_excavate_the_hill_of_sorcery",
"DGU_clear_the_ruins",
"DGU_lay_the_foundations",
"DGU_expand_the_thrall_pits",
"DGU_the_creeping_gloom",
"DGU_the_masters_of_the_mirkwood",
"DGU_a_reward_from_mordor",
"DGU_shadow_without_master",
"DGU_treat_with_the_spawn_of_ungoliant",
"DGU_salvage_the_ruins",
"DGU_restore_the_dungeons",
"DGU_whispers_in_the_boughs",
"DGU_centralize_military_planning",
"DGU_master_of_the_fortress",
"DGU_purge_the_eyes_faithful",
"DGU_dark_constructs",
"DGU_fortify_the_naked_hill",
"DGU_territorial_incursions",
"DGU_spur_the_spawn_of_ungoliant",
"DGU_a_guise_of_sorcery",
"DGU_the_veil_against_the_golden_wood",
"DGU_subjugate_the_spiders",
"DGU_restore_the_fortress",
"DGU_construction_efforts",
"DGU_improve_the_design",
"DGU_black_smoke_rises",
"DGU_inner_chamber_storage",
"DGU_flesh_sculpting_pits",
"DGU_prepare_a_ring_interception",
"DGU_focus_on_lothlorien",
"DGU_focus_on_mirkwood",
"DGU_the_assault_on_lorien",
"DGU_secure_the_outskirts",
"DGU_thurst_north",
"DGU_probing_raids",
"DGU_elves_in_chains",
"DGU_offer_support",
"DGU_to_the_mountains_and_beyond",
"DGU_seek_help_from_goblin_town",
"DGU_invasion",
"DGU_coordinate_with_gundabad",
"DGU_sabotage_supplies",
"DGU_prepare_a_supplyline_roh",
"DGU_fall_upon_the_wold",
"DGU_study_rohirrim_tactics",
"DGU_coordinate_with_isengard",
"DGU_occupy_the_outskirts",
"DGU_cavalry_innovations",
"DGU_shared_army_exercises",
"DGU_threaten_the_east",
"DGU_secure_southern_mirkwood",
"DGU_forge_eastwards",
"DGU_coordinate_with_rhun",
"DGU_prepare_a_supplyline",
"DGU_raid_the_fields_of_rhovanion",
"DGU_topple_the_old_kingdom",
"DGU_a_well_timed_distraction",
"DGU_build_up_our_forces",
"DGU_secret_army_drills",
"DGU_secure_a_perimeter",
"DGU_await_the_signal",
"DGU_in_all_directions",
"DGU_enslave_the_spiders",
"DGU_quell_the_infighting",
"DGU_meat_from_mordor",
"DGU_specialized_equipment",
"DGU_better_army_leaders",
"DGU_the_iron_crown_of_mirkwood",
"DGU_ward_against_the_east",
"DGU_the_twilight_dominion",
"DGU_reasearch_and_misc",
"DGU_jagged_steel",
"DGU_hammers_of_amon_lanc",
"DGU_black_iron_casting",
"DGU_black_fletching",
"DGU_construction_efforts_cBi347",
"DGU_spider_venom_dipping",
"DGU_machines_of_war",
"DGU_war_riders_of_the_dark_hill",
"DGU_fellbeast_supremacy",
"DGU_aggressive_expansion",
"DGU_creeping_presence",
"DGU_learn_from_our_raids",
"DGU_an_audacious_move",
"DGU_southern_consolidation",
"DGU_local_propaganda",
"DGU_resistance_suppression",
"DGU_resource_extraction",
"DGU_local_recruitment",
"DGU_establish_a_supplyline",
"DGU_unlock_mordors_knowledge",
"DGU_forest_of_shadows",
"DGU_extra_research_slot",
"DGU_unitary_initiatives",
"DGU_consolidate_the_guilds",
"DGU_consolidate_intelligence",
"DGU_black_market_trading",
"DGU_deep_forest_farming",
"DGU_knowledge_preservation",
"DGU_economic_consolidation",
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