

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
                        "file_uri": "https://generativelanguage.googleapis.com/v1beta/files/1a4m06co36n8", 
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

I'm currently working on a focus tree for the Spiders of the Mirkwood.
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
("SPI_hunger", "Hunger"),
("SPI_cannibalistic_tendencies", "Cannibalistic Tendencies"),
("SPI_feed_and_breed", "Feed and Breed"),
("SPI_call_up_the_hatchlings", "Call Up the Hatchlings"),
("SPI_let_eggs_mature", "Let Eggs Mature"),
("SPI_the_great_feast", "The Great Feast"),
("SPI_the_brood_lairs", "The Brood Lairs"),
("SPI_the_colony_wakes", "The Colony Wakes"),
("SPI_the_spiders_nest", "The Spiders' Nest"),
("SPI_the_mothers_guard", "The Mother's Guard"),
("SPI_control_over_mirkwood", "Control Over Mirkwood"),
("SPI_defensive_stance", "Defensive Stance"),
("SPI_aggresive_stance", "Aggressive Stance"),
("SPI_step_out_of_the_shadows", "Step Out of the Shadows"),
("SPI_hierarchy_order", "Hierarchy Order"),
("SPI_subdue_the_lesser_broods", "Subdue the Lesser Broods"),
("SPI_heed_the_necromancer", "Heed the Necromancer"),
("SPI_hatred_of_the_bright_folk", "Hatred of the Bright Folk"),
("SPI_the_taste_of_stone_flesh", "The Taste of Stone-Flesh"),
("SPI_stench_of_the_rotten", "Stench of the Rotten"),
("SPI_light_and_shadow", "Light and Shadow"),
("SPI_return_of_night_mother_shelob", "Return of Night Mother Shelob"),
("SPI_daughter_of_ungoliant", "Daughter of Ungoliant"),
("SPI_control_all_mirkwood", "Control All Mirkwood"),
("SPI_ensnare_the_invaders", "Ensnare the Invaders"),
("SPI_aerial_webwalls", "Aerial Web-Walls"),
("SPI_ascension_of_a_brood_leader", "Ascension of a Brood Leader"),
("SPI_through_cannibal_rites", "Through Cannibal Rites"),
("SPI_through_silent_communion", "Through Silent Communion"),
("SPI_the_alpha_hunter", "The Alpha Hunter"),
("SPI_endless_struggle", "Endless Struggle"),
("SPI_the_great_weaver", "The Great Weaver"),
("SPI_the_dream_weaver", "The Dream Weaver"),
("SPI_harmonize_the_instincts", "Harmonize the Instincts"),
("SPI_broodmothers_woodland", "Broodmother's Woodland"),
("SPI_arachnid_nature", "Arachnid Nature"),
("SPI_matriarchs_court", "Matriarch's Court"),
("SPI_guidance_of_fury", "Guidance of Fury"),
("SPI_pheromonal_harmony", "Pheromonal Harmony"),
("SPI_the_queens_will", "The Queen's Will"),
("SPI_exalt_the_brood_warriors", "Exalt the Brood Warriors"),
("SPI_architects_of_silk", "Architects of Silk"),
("SPI_let_roam_the_brood", "Let Roam the Brood"),
("SPI_consume_the_light", "Consume the Light"),
("SPI_build_up_defenses", "Build Up Defenses"),
("SPI_silk_spun_workshops", "Silk-Spun Workshops"),
("SPI_underground_colonies", "Underground Colonies"),
("SPI_expand_the_brood_burrows", "Expand the Brood Burrows"),
("SPI_deepening_the_nest", "Deepening the Nest"),
("SPI_alliance_building", "Alliance Building"),
("SPI_direct_the_hunting_brood", "Direct the Hunting Brood"),
("SPI_proliferation_of_the_swarm", "Proliferation of the Swarm"),
("SPI_grand_ambitions", "Grand Ambitions"),
("SPI_world_wide_web", "World Wide Web"),
("SPI_seek_new_knowledge", "Seek New Knowledge"),
("SPI_sharpened_fangs", "Sharpened Fangs"),
("SPI_volatile_gland_experiments", "Volatile Gland Experiments"),
("SPI_arachnid_engineering", "Arachnid Engineering"),
("SPI_whispers_in_the_webs", "Whispers in the Webs"),
("SPI_perfected_predation", "Perfected Predation"),
("SPI_enhanced_corrosive_force", "Enhanced Corrosive Force"),
("SPI_webbound_mechanica", "Webbound Mechanica"),
("SPI_dark_brood_sorcery", "Dark Brood Sorcery"),
("SPI_web_wisdom_converged", "Web Wisdom Converged"),
("SPI_focus_on_the_essentials", "Focus on the Essentials"),
("SPI_study_the_two_leggeds", "Study the Two-Leggeds"),
("SPI_the_errant_visionaries", "The Errant Visionaries"),
("SPI_mastery_of_our_nature", "Mastery of Our Nature"),
("SPI_matriphagy", "Matriphagy"),
("SPI_we_spin_our_own_threads", "We Spin Our Own Threads"),
("SPI_hungering_for_the_riverlands", "Hungering for the Riverlands"),
("SPI_protect_the_egg_chambers", "Protect the Egg Chambers"),
("SPI_harvests_of_the_deep_nest", "Harvests of the Deep Nest"),
("SPI_forging_the_fangpits", "Forging the Fangpits"),
("SPI_evolve_the_nests_cunning", "Evolve the Nest's Cunning"),
("SPI_expand_the_nest", "Expand the Nest"),
("SPI_erratic_ascendance", "Erratic Ascendance"),
("SPI_measured_mutations", "Measured Mutations"),
("SPI_gifts_from_the_dark_tower", "Gifts from the Dark Tower"),
("SPI_send_tribute_to_baraddur", "Send Tribute to Barad-dûr"),
("SPI_settle_territorial_disputes", "Settle Territorial Disputes"),
("SPI_wisdom_for_knowledge", "Wisdom for Knowledge"),
("SPI_flesh_for_peace", "Flesh for Peace"),
("SPI_alliance_of_the_deep_woods", "Alliance of the Deep Woods"),
("SPI_look_west_for_aid", "Look West for Aid"),
("SPI_pact_of_shadows", "Pact of Shadows"),
("SPI_the_great_weave", "The Great Weave"),
("SPI_restrain_the_hunger", "Restrain the Hunger"),
("SPI_carpaces_and_fangs", "Carpaces and Fangs"),
("SPI_adaptive_learning", "Adaptive Learning"),
("SPI_devour_the_deep_kin", "Devour the Deep Kin"),
("SPI_feast_on_the_fair", "Feast on the Fair"),
("SPI_webs_over_the_black_tower", "Webs Over the Black Tower"),
("SPI_delicous_warm_blood", "Delicious Warm Blood"),
("SPI_economy_of_hunger", "Economy of Hunger"),
("SPI_rouse_the_war_broods", "Rouse the War Broods"),
("SPI_strike_north", "Strike North"),
("SPI_recall_the_roaming_brood", "Recall the Roaming Brood"),
("SPI_move_south", "Move South"),
("SPI_secure_the_north", "Secure the North"),
("SPI_endless_sprawl", "Endless Sprawl"),
("SPI_secure_the_south", "Secure the South"),
("SPI_purge_the_two_leggeds", "Purge the Two-Leggeds"),
("SPI_the_great_nest", "The Great Nest"),
("SPI_assert_out_control", "Assert Our Control"),
("SPI_the_one_ring_gambit", "The One Ring Gambit"),
("SPI_put_our_differences_aside", "Put Our Differences Aside"),
("SPI_ungoliants_apetite", "Ungoliant's Appetite"),
("SPI_tender_flesh", "Tender Flesh"),
("SPI_black_blood", "Black Blood"),
("SPI_extend_the_perimeter", "Extend the Perimeter"),
("SPI_ecdysis", "Ecdysis"),
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