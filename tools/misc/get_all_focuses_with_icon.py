



from pdx_parser import *


focus_path = r'common\national_focus\mirkwood.txt'

focuses = ParseObjFromFile(focus_path).GetAll("focus").value

icon_to_search = "GFX_unknown_focus"

for focus in focuses:
    if focus.Has("icon") and focus.GetVal("icon") == icon_to_search:
        print(focus.GetVal("id"))
    
