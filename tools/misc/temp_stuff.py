


text = """
$TOKEN$ = {
    track = archers_mounted_track
    name = SUBDOCTRINE_$TOKEN$
    description = SUBDOCTRINE_$TOKEN$_DESC
    icon = GFX_forward_interception_medium

    xp_cost = 100
    xp_type = army

    available = {
        always = yes
    }

    ai_will_do = { }

    # EFFECTS
	# TODO

    rewards = {
		# TODO
    }
}
"""


nlist = [
	"crossbow_levies",
	"elusive_skirmishers",
	"archer_lines_integration",
	"mobile_archers",
]


for name in nlist:
    print(text.replace("$TOKEN$", name))
    print("\n\n")