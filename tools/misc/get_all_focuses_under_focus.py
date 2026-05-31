



from pdx_parser import *


focus_path = r'common\national_focus\spiders.txt'

root_focus_name = "SPI_ascension_of_a_brood_leader"

focus_tree = ParseObjFromFile(focus_path)

child_focuses = set()

child_focuses.add(root_focus_name)

prev_child_focuses_len = 0

while len(child_focuses) > prev_child_focuses_len:

    prev_child_focuses_len = len(child_focuses)

    for focus in focus_tree.GetAll("focus").value:
        if focus.GetVal("id") in child_focuses:
            continue
        elif focus.Has("prerequisite"):
            for preq in focus.Get("prerequisite").value:
                if preq.value in child_focuses:
                    child_focuses.add(focus.GetVal("id"))
                    break
        
for f in child_focuses:
    print(f)

    
