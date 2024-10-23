import pyperclip


project_title = "Resist Heat"
project_title_token = "sp_resist_heat_spell"

rewards = [
    {
        "reward_title": "[Character.GetName] proposes modifying the heat resistance spell.",
        "reward_title_token": "sp_resist_heat_modification",
        "reward_desc": "As the spell nears completion, [Character.GetName] suggests altering the enchantment to enhance our troops' ability to withstand extreme heat. However, this change might reduce their tolerance to colder climates, which could be a disadvantage in certain regions.",
        "reward_min_threshold": "0",
        "reward_max_threshold": "100",
        "reward_weight": "100",

        "options": [
            ("sp_resist_heat_modification_yes", "Increase acclimatization to heat at the cost of cold resistance."),
            ("sp_resist_heat_modification_no", "Maintain balanced resistance to all climates."),
        ]
    }
]









project_template = """
$project_title_token$ = {

	specialization = specialization_laboratory

	project_tags = sp_tag_artillery

	allowed = {
		# TODO
	}

	visible = {
		# TODO
	}
	
	available = {
		FROM = {
			# TODO
		}
	}
	
	prototype_time = sp_time.prototype.short # TODO
	complexity = sp_complexity.medium # TODO

	breakthrough_cost = {
		specialization_laboratory = 2 # TODO
	}

	resource_cost = {
		# resources = { steel=4 chromium=2 } # TODO
	}
	
	project_output = {
		# TODO
	}

	generic_prototype_rewards = { # TODO
		sp_generic_reward_scientist_xp_1
        sp_generic_reward_scientist_xp_2
        sp_generic_reward_scientist_xp_3
        sp_generic_reward_army_xp_1
        sp_generic_reward_army_xp_2
        sp_generic_reward_army_xp_3
        sp_generic_reward_navy_xp_1
        sp_generic_reward_navy_xp_2
        sp_generic_reward_navy_xp_3
        sp_generic_reward_air_xp_1
        sp_generic_reward_air_xp_2
        sp_generic_reward_air_xp_3
        sp_generic_reward_major_progress_1
        sp_generic_reward_major_progress_2
        sp_generic_reward_major_progress_3
        sp_generic_reward_test_failure_1
        sp_generic_reward_test_failure_2
        sp_generic_reward_test_failure_3
        sp_generic_reward_resource_scarcity
        sp_generic_reward_critical_failure
        sp_generic_reward_political_interference
        sp_generic_reward_major_failure
        sp_generic_reward_minor_explosion
        sp_generic_reward_fire
        sp_generic_reward_infantry_weapons_tech
        sp_generic_reward_infantry_archery_tech
        sp_generic_reward_support_tech_tech
        sp_generic_reward_cavalry_tech
        sp_generic_reward_machines_siege_equipment_tech
        sp_generic_reward_knowledge_alchemy_tech
        sp_generic_reward_knowledge_magic_tech
        sp_generic_reward_knowledge_scriptorium_tech
        sp_generic_reward_knowledge_intrigue_tech
        sp_generic_reward_labour_metalworking_tech
        sp_generic_reward_labour_metalworking_mining_tech
        sp_generic_reward_labour_construction_tech
        sp_generic_reward_labour_farming_tech
        sp_generic_reward_sailing_tech
        sp_generic_reward_eagles_tech
        sp_generic_reward_fellbeasts_tech
        sp_generic_reward_elven_secrets_tech
        sp_generic_reward_dwarven_secrets_tech
        sp_generic_reward_men_secrets_tech
        sp_generic_reward_orcs_secrets_tech
	}

	unique_prototype_rewards = {

		$REWARDS$
	}
}

"""


reward_template = """
		$UNIQUE_REWARD_TOKEN$ = {
			fire_only_once = yes

			threshold = { 
				min = $UNIQUE_REWARD_MIN_THRESHOLD$
				max = $UNIQUE_REWARD_MAX_THRESHOLD$
			}

			weight = {
				base = $UNIQUE_REWARD_WEIGHT$
			}

			$REWARD_OPTIONS$
        }
"""

option_template = """
			option = {
				token = $reward_option_token$
				
				iteration_output = {
					# TODO
				}
			}
"""



# SPECIAL PROJECT DEF

rewards_str = ""
for rew in rewards:

    options_str = ""
    for (opt_token, opt_loc) in rew["options"]:
        options_str += option_template.replace("$reward_option_token$", opt_token)

    rewards_str += reward_template.replace("$REWARD_OPTIONS$", options_str).replace("$UNIQUE_REWARD_MIN_THRESHOLD$", rew["reward_min_threshold"]).replace("$UNIQUE_REWARD_MAX_THRESHOLD$", rew["reward_max_threshold"]).replace("$UNIQUE_REWARD_WEIGHT$", rew["reward_weight"]).replace("$UNIQUE_REWARD_TOKEN$", rew["reward_title_token"])

ret = project_template.replace("$REWARDS$", rewards_str).replace("$project_title_token$", project_title_token)

#print(ret)

#pyperclip.copy(ret)




# LOCS
locs  = f"{project_title_token}:0 \"{project_title}\"\n"

for rew in rewards:
    locs += f'{rew["reward_title_token"]}:0 \"{rew["reward_title"]}\"\n'
    locs += f'{rew["reward_title_token"]}_desc:0 \"{rew["reward_desc"]}\"\n'

    for (opt_token, opt_loc) in rew["options"]:
        locs += f"{opt_token}:0 \"{opt_loc}\"\n"

pyperclip.copy(ret + "\n\n" + locs)






