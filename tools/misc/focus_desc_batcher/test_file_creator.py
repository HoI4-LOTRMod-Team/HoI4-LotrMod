

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/vst4h6wcnrga", 
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

I'm currently working on a focus tree for Gundabad, which can stay as orcs or go down a 'Gundabad Expedition' path, where either dwarves or men reclaim it.
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
Note that this focuses true name is actually 'TRUE_NAME' (PROMPT is the id).

Provide me the descriptions in the following format:

focus_name_desc:0 "focus description 1"
focus_name_desc:0 "focus description 2"
focus_name_desc:0 "focus description 3"
focus_name_desc:0 "focus description 4"
focus_name_desc:0 "focus description 5"

Provide only this list of descriptions and no other text at all.
"""

prompt_list = [
("GUN_workers_and_soldiers", "Workers and Soldiers"),
("GUN_restore_diplomatic_efforts", "Restore Diplomatic Efforts"),
("GUN_restore_dwarven_architecture", "Restore Dwarven Architecture"),
("GUN_dwarven_miners_guilds", "Dwarven Miner's Guild"),
("GUN_secure_foreign_support", "Secure Foreign Support"),
("GUN_convene_a_secret_council", "Convene a Secret Council"),
("GUN_rally_the_scattered_longbeards", "Rally the Scattered Longbeards"),
("GUN_gather_eotheod_descendants", "Gather Éotheod Descendants"),
("GUN_survey_the_old_tunnels", "Survey the Old Tunnels"),
("GUN_invoke_the_memory_of_fram", "Invite the Memory of Fram"),
("GUN_rally_nearby_support", "Rally Local Support"),
("GUN_exasperate_orc_infighting", "Stoke Orcish Infighting"),
("GUN_mountain_specialists", "Mountain Specialists"),
("GUN_mass_deployments", "Mass Deployments"),
("GUN_elite_formations", "Elite Formations"),
("GUN_large_army_efforts", "Large Army Efforts"),
("GUN_light_cavalry", "Light Cavalry"),
("GUN_heavy_cavalry", "Heavy Cavalry"),
("GUN_establish_an_administration", "Establish An Administration"),
("GUN_equipment_effort_2", "Equipment Effort II"),
("GUN_siege_machinery", "Siege Machinery"),
("GUN_support_equipment", "Support Equipment"),
("GUN_doctrine_effort_2", "Doctrine Effort II"),
("GUN_move_on", "Leave the Past Behind"),
("GUN_reorgnaize_military_facilities", "Reorganize Military Facilities"),
("GUN_local_ambitions", "Local Ambitions"),
("GUN_raise_a_new_army", "Raise a New Army"),
("GUN_seek_out_new_spoils", "Seek Out New Spoils"),
("GUN_quest_for_vengeance", "Quest for Vengeance"),
("GUN_contact_collaborators", "Contact Collaborators"),
("GUN_subjugate_the_beornings", "Subjugate the Beornings"),
("GUN_align_the_beornings", "Align the Beornings"),
("GUN_vengeance_at_last", "Vengeance, at Last"),
("GUN_turn_west", "Turn West"),
("GUN_turn_south", "Turn South"),
("GUN_war_with_angmar", "War With Angmar"),
("GUN_war_with_the_beornings", "War With the Beornings"),
("GUN_claim_rhudaur_territory", "Claim Rhudaur Land"),
("GUN_align_the_goblins", "Align the Mountain Goblins"),
("GUN_forceful_integration", "Forceful Integration"),
("GUN_consolidate_our_hold", "Consolidate Our Hold"),
("GUN_secret_knowledge_acquisition", "Secret Knowledge Aquisition"),
("GUN_political_alignment", "Political Alignment"),
("GUN_consolidate_leadership", "Consolidate Leadership"),
("GUN_speed_up_industry", "Speed Up Industry Efforts"),
("GUN_speed_up_mobilization", "Speed Up Mobilization"),
("GUN_deface_azogs_legacy", "Deface Azog's Legacy"),
("GUN_ransack_the_depots", "Ransack the Supply Depots"),
("GUN_decentralized_army_leadership", "Decentralized Army Leadership"),
("GUN_no_laws_or_gods", "No Laws or Kings"),
("GUN_repurpose_workshops", "Repurpose Workshops"),
("GUN_no_kings", "No Crowns on the Mountain"),
("GUN_mobilize_the_masses", "Mobilize the Masses"),
("GUN_contribution_systems", "Contribution Systems"),
("GUN_raid_the_surroundings", "Raid the Surroundings"),
("GUN_mob_rule", "Mob Rule"),
("GUN_fortify_the_border", "Fortify the Border"),
("GUN_trolls_from_mordor", "Trolls from Mordor"),
("GUN_local_recruitment", "Local Recruitment Efforts"),
("GUN_wizards_sorcery", "Saruman's Sorcery"),
("GUN_self_sufficiency_focus", "Self-Sufficiency Focus"),
("GUN_fellbeast_supremacy", "Fellbeast Supremacy"),
("GUN_request_mithril_mining_experts", "Request Mithril Mining Experts"),
("GUN_mithril_metalwork", "Mithril Metalwork"),
("GUN_countryside_markets", "Countryside Markets"),
("GUN_pride_restored", "Pride Restored"),
("GUN_secure_support_from_gladden", "Secure Support from Gladden"),
("GUN_forodwaithi_support", "Forodwaithi Support"),
("GUN_prepare_to_seize_orc_armories", "Prepare to Seize Orc Armories"),
("GUN_plan_a_swift_assault", "Plan a Swift Assault"),
("GUN_a_symbol_of_hope", "A Symbol of Hope"),
("GUN_food_silos", "Grain Silos"),
("GUN_honeycakes_and_hardiness", "Honeycakes and Hardiness"),
("GUN_expand_recruitment", "Expand Recruitment"),
("GUN_military_research_focus", "Military Research Focus"),
("GUN_civilian_research_focus", "Civlian Research Focus"),
("GUN_supply_the_moving_front", "Supply the Moving Front"),
("GUN_send_aid_to_moria", "Send Aid to Moria"),
]

requests_list = [

]


i = 1
for (prompt, tn) in prompt_list:
    p = prompt_template.replace("PROMPT", prompt).replace("TRUE_NAME", tn)

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