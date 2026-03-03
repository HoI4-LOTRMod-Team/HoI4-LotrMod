

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
("GUN_the_fate_of_gundabad", "The Fate of Gundabad"),
("GUN_army_effort", "Army Effort"),
("GUN_equipment_effort", "Equipment Effort"),
("GUN_cavalry_effort", "Cavalry Effort"),
("GUN_doctrine_effort", "Doctrine Effort"),
("GUN_infrastructure_investment", "Infrastructure Investment"),
("GUN_more_production_research", "More production research"),
("GUN_civilian_production", "Civilian Production"),
("GUN_more_civilian_production", "More Civilian Production"),
("GUN_military_production", "Military Production"),
("GUN_more_military_production", "More Military Production"),
("GUN_focus_on_civilian_industry", "Prioritize Civilian Industry"),
("GUN_focus_on_military_industry", "Prioritize Military Industry"),
("GUN_make_room_in_the_mountain", "Make room in the Mountain"),
("GUN_settle_our_internal_economy", "Settle our Internal Economy"),
("GUN_the_orcs_of_the_north", "The Orcs of the North"),
("GUN_follow_the_strong", "Rule of Strength"),
("GUN_restore_border_outposts", "Restore Border Outposts"),
("GUN_reinvigorate_the_broken_realm", "Reinvigorate Broken Spirits"),
("GUN_spread_gradual_propaganda", "Slow Burning Flame"),
("GUN_hate_and_violence", "Rage and Contempt"),
("GUN_strengthen_our_leadership", "Empower Army Leaders"),
("GUN_the_reawakened_kingdom", "The Reawakened Kingdom"),
("GUN_exert_the_wrath_of_the_orcs", "Exert the Wrath of the Orcs"),
("GUN_declare_a_new_king_of_orcs", "Declare a new King of Orcs"),
("GUN_legacy_of_azog", "The Legacy of Azog"),
("GUN_we_need_not_follow_others", "We Break Before We Bend"),
("GUN_the_strength_of_others", "Strength in Allies"),
("GUN_follow_angmar", "Follow Angmar"),
("GUN_bow_to_saruman", "Bow to the White Wizard"),
("GUN_join_sauron", "Submit to the Dark Lord"),
("GUN_mutiny", "Mutiny!"),
("GUN_strength_in_numbers", "Strength in Numbers"),
("GUN_no_more_boldogs", "No more Boldogs"),
("GUN_the_orc_revolution_abroad", "Support Orc Insurrections"),
("GUN_depose_the_old_government", "Depose the old government"),
("GUN_join_mordors_revolution", "Join the Orcs of Mordor"),
("GUN_invite_moria_orcs", "Invite the Orcs of Moria"),
("GUN_wary_of_the_necromancer", "Be Wary of the Necromancer"),
("GUN_he_must_be_defeated", "Resist Sauron's Will"),
("GUN_sauron_will_fall", "Topple the Dark Lord"),
("GUN_remember_the_battle", "Remember the Defeat"),
("GUN_restart_the_forges", "Restart the Forges"),
("GUN_distant_campaigns", "Distant Campaigns"),
("GUN_victory_or_death", "Victory or Death"),
("GUN_vengeance_on_erebor", "Attack the Lonely Mountain"),
("GUN_target_thranduil", "Assault the Elven King's Halls"),
("GUN_destroy_the_bardings", "Destroy the Bardings"),
("GUN_the_gundabad_expedition", "The Gundabad Expedition"),
("GUN_a_message_to_angmar", "Seek Angmar's Support"),
("GUN_a_message_to_beorn", "Seek Beorning Support"),
("GUN_a_message_to_erebor", "Secure Support from Erebor"),
("GUN_locate_weakspots", "Locate Weakspots"),
("GUN_spy_on_the_orcs", "Spy on the Orcs"),
("GUN_infiltrate_the_orcs", "Infiltrate the Orcs"),
("GUN_raid_orc_infrastructure", "Raid Orcish Supplylines"),
("GUN_the_new_inhabitants", "Reclaim the Fortress"),
("GUN_the_dwarves_of_gundabad", "The Dwarves of Gundabad"),
("GUN_home_of_the_dwarves", "Home of the Dwarves"),
("GUN_mine_for_mithril", "Mine for Mithril"),
("GUN_reignite_the_old_forges", "Reignite the Old Forges"),
("GUN_reopen_the_old_mines", "Reopen the Old Mines"),
("GUN_the_gold_trade", "The Gold Trade"),
("GUN_further_iron_mining", "Expand Iron Mining"),
("GUN_join_erebor", "Join Erebor"),
("GUN_befriend_durin", "Befriend Durin"),
("GUN_invite_him_to_our_faction", "Join Causes with Ered Luin"),
("GUN_the_men_of_gundabad", "The Men of Gundabad"),
("GUN_human_lead_industry", "Mannish Industry"),
("GUN_welcome_more_people", "Invite More Settlers"),
("GUN_join_angmar", "Join Angmar"),
("GUN_form_a_militia_battalion", "Form a Militia Battalion"),
("GUN_the_victorious_expedition", "A Victorious Expedition"),
("GUN_a_hardy_people", "A Hardy People"),
("GUN_a_strong_new_government", "Inspirational Leadership"),
("GUN_the_expeditions_knowledge", "The Expedition's Knowledge"),
("GUN_hunt_down_the_orcs", "Hunt Down Orc Stragglers"),
("GUN_restore_the_old_fortress", "Restore the Fortress"),
("GUN_join_gondor", "Join Gondor"),
("GUN_restore_gundabad_industry", "Restore Gundabad Industry"),
("GUN_repay_our_supporters", "Repay Our Supporters"),
("GUN_the_mountain_research_institute", "The Mountain Library"),
("GUN_products_of_research", "Products of Research"),
("GUN_farming_efforts", "Farming Efforts"),
("GUN_leather_tanneries", "Leather Tanneries"),
("GUN_build_a_new_army", "Build a new Army"),
("GUN_get_rid_of_all_the_orcs", "Preemptive Strikes"),
("GUN_train_mountaineers", "Train Mountaineers"),
("GUN_dwarven_human_cooperation", "Dwarven-Mannish Cooperation"),
("GUN_the_skies_above", "The Skies Above"),
("GUN_a_friendship_with_the_eagles", "Friendship With the Eagles"),
("GUN_trade_with_the_woodsmen", "Trade with the Woodmen"),
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