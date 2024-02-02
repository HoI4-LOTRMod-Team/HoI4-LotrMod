NDefines.NGame.START_DATE = "3018.1.1.12"
NDefines.NGame.END_DATE = "4018.1.1.1"
NDefines.NGame.HANDS_OFF_START_TAG = "RHD"

NDefines.NAI.HIGH_COMMAND_ADDED_WEIGHT_FACTOR = 0.5	-- Weight multiplier for high_command advisors over other chosen advisor or idea types
NDefines.NAI.CHIEF_ADDED_WEIGHT_FACTOR = 1.0			-- Weight multiplier for chief roles over other advisor or idea types
NDefines.NAI.ADVISOR_SCORE_CHEAPER_IS_BETTER_FACTOR = 0.5  -- When scoring advisors, this define scales how much the AI prefers cheaper advisors over more expensive ones. 0.0 means no effect, 0.15 means a cost difference of 100 PP modifies the score by 15 %.
NDefines.NAI.DESIGN_COMPANY_SCORE_MULTIPLIER = 1.25              -- score multiplier for hiring a design company
NDefines.NAI.ARMY_CHIEF_SCORE_MULTIPLIER = 0.75                  -- score multiplier for hiring an army chief
NDefines.NAI.AIR_CHIEF_SCORE_MULTIPLIER = 1.0                   -- score multiplier for hiring an air chief
NDefines.NAI.POLITICAL_ADVISOR_SCORE_MULTIPLIER = 1.25           -- score multiplier for hiring political advisors

NDefines.NOperatives.AGENCY_CREATION_FACTORIES = 3					-- Number of factories used to create an intelligence agency


NDefines.NCharacter.OFFICER_CORP_ADVISOR_ENTRIES_IN_MENU = { "high_command", "theorist", "army_chief", "cavalry_chief", "navy_chief" }
NDefines.NCharacter.OFFICER_CORP_HIGH_COMMAND_SLOTS_IN_MENU = 2 --For Alert manager to count the number of High Command Slots in the UI
NDefines.NCharacter.POLITICAL_ADVISOR_SLOTS_IN_MENU = 2 --For Alert manager to count the number of Political Advisor Slots in the UI
NDefines.NCharacter.DEFAULT_PP_COST_FOR_MILITARY_ADVISOR = 150	-- When an advisor does not have cost assigned this is the default used	
NDefines.NCharacter.SPECIALIST_ADVISOR_MIN_RANK = 3
NDefines.NCharacter.EXPERT_ADVISOR_MIN_RANK = 5
NDefines.NCharacter.GENIUS_ADVISOR_MIN_RANK = 7

NDefines.NMilitary.SLOWEST_SPEED = 3


NDefines.NMilitary.BASE_FORT_PENALTY = -0.4

NDefines.NBuildings.AIRBASE_CAPACITY_MULT = 10


NDefines.NNavy.SHORE_BOMBARDMENT_CAP = 0.75
NDefines.NNavy.HEAVY_GUN_ATTACK_TO_SHORE_BOMBARDMENT = 0.3  -- heavy gun attack value is divided by this value * 100 and added to shore bombardment modifier
NDefines.NNavy.LIGHT_GUN_ATTACK_TO_SHORE_BOMBARDMENT = 0.15 -- light gun attack value is divided by this value * 100 and added to shore bombardment modifier