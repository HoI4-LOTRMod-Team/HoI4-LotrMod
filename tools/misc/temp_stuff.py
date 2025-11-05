


text = """
$TOKEN$ = {
    name = DOCTRINE_TRACK_$TOKEN$
    background = "GFX_air_superiority_bg"
    background_offset = 0
    icon = "GFX_doctrine_milestone_fighter_air"
    icon_frame = "GFX_infantry_doctrine_deco"
    mastery = {
        multiplier = 5.0
        categories = {
            category_all_infantry
        }
    }
}
"""


nlist = [
		'dav_infantry_track',
        'dav_archers_track',
        'dav_cavalry_track',
        'dav_machs_track',
		'horde_infantry_track',
        'horde_archers_track',
        'horde_cavalry_track',
        'horde_machs_track',
		'sws_infantry_track',
        'sws_archers_track',
        'sws_cavalry_track',
        'sws_machs_track',
		'maw_infantry_tack',
        'maw_archers_track',
        'maw_cavalry_track',
        'maw_machs_track',
]


for name in nlist:
    print(text.replace("$TOKEN$", name))
    print("\n\n")