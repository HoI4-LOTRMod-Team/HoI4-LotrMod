

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/t47xtdfdycwo", 
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
("RHUN_handle_logathvuld", "Handle Logathvuld"),
("RHUN_strongarm_diplomacy", "Strongarm Diplomacy"),
("RHUN_demand_a_settlement", "Demand a Settlement"),
("RHUN_align_logathvuld", "Align Logathvuld"),
("RHUN_merge_administrations", "Merge Administrations"),
("RHUN_crack_down_on_resistance", "Crack Down on Resistance"),
("RHUN_the_western_thrust", "The Western Thrust"),
("RHUN_antagonize_dale_and_erebor", "Antagonize Dale and Erebor"),
("RHUN_the_path_to_mirkwood", "The Path to Mirkwood"),
("RHUN_take_matters_into_our_own_hands", "Take Matters into Our Own Hands"),
("RHUN_wood_skirmishing_tactics", "Forest Skirmishing Tactics"),
("RHUN_economy_of_conquest", "Economy of Conquest"),
("RHUN_seize_the_marshes", "Seize the Marshes"),
("RHUN_focus_on_dale", "Focus on Dale"),
("RHUN_territorial_expansion", "Territorial Expansion"),
("RHUN_army_of_conquest", "Army of Conquest"),
("RHUN_settle_the_land", "Settle the Land"),
("RHUN_deal_with_the_dwarves", "Deal with the Dwarves"),
("RHUN_fortify_the_southern_border", "Fortify the Southern Border"),
("RHUN_deter_the_lord_of_mordor", "Deter the Lord of Mordor"),
("RHUN_palace_politics", "Palace Politics"),
("RHUN_backstabbing_and_treachery", "Backstabbing and Treachery"),
("RHUN_replace_nepotistic_army_leaders", "Replace Nepotistic Army Leaders"),
("RHUN_accelerate_decision_making", "Accelerate Decision Making"),
("RHUN_purge_corrupt_officials", "Purge Corrupt Officials"),
("RHUN_bribe_laketown_delegates", "Bribe Laketown Delegates"),
("RHUN_bribe_dwarven_envoys", "Bribe Dwarven Envoys"),
("DRH_restore_stability", "Restore Stability"),
("DRH_restore_diplomatic_channels", "Restore Diplomatic Channels"),
("DRH_path_to_revancha", "The Path to Revenge"),
("DRH_seek_protection_from_dale", "Seek Protection From Dale"),
("DRH_rebuild_forces", "Rebuild Our Forces"),
("DRH_ally_with_logath", "Ally With Logath"),
("DRH_break_the_treaty", "Break the Treaty"),
("DRH_resume_research_efforts", "Resume Research Efforts"),
("DRH_join_the_dwarves", "Join the Dwarves"),
("DRH_deterrence", "Deterrence"),
("DRH_maintain_military_formations", "Maintain Military Formations"),
("DRH_restore_a_stable_admin", "Restore a Stable Administration"),
("DRH_beacon_of_freedom", "Beacon of Freedom"),
("DRH_set_up_southern_supplylines", "Set Up Southern Supplylines"),
("DRH_scholarly_endeavours", "Scholarly Endeavours"),
("RHUN_cavalry_focus", "Cavalry Focus"),
("RHUN_doctrine_focus", "Doctrine Focus"),
("RHUN_doctrine_focus_2", "Advance Military Theory"),
("RHUN_infantry_modernization", "Infantry Modernization"),
("RHUN_eastern_adaptations", "Eastern Adaptations"),
("RHUN_logathin_scholars", "Logathin Scholars"),
("RHUN_wipe_out_the_seccesionists", "Wipe Out the Secessionists"),
("RHUN_contact_the_avari", "Contact the Avari"),
("RHUN_secure_the_oracarni", "Secure the Oracarni"),
("DRH_integrate_the_eastern_tribes", "Integrate the Eastern Tribes"),
("RHUN_reallocate_civilian_resources", "Reallocate Civilian Resources"),
("RHUN_demand_submission", "Demand Submission"),
("RHUN_request_khand_autonomy", "Request Khand Autonomy"),
("RHUN_trade_with_the_variags", "Trade With the Variags"),
("RHUN_negotiate_resource_rights", "Negotiate Resource Rights"),
("RHUN_reward_from_mordor", "The Dark Lord's Reward"),
("RHUN_join_forces_with_mordor", "Join Forces With Mordor"),
("RHUN_form_a_faction", "Form a Faction"),
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