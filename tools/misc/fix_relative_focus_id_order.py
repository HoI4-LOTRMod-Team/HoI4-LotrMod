from pdx_parser import *


filepath = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\rhun.txt'

root_obj = ParseListFromFile_asPObj(filepath)


focus_rel = {}

for focus in root_obj.Get("focus_tree").value:
    if focus.id == "focus":

        if focus.Has("relative_position_id"):
            focus_rel[focus.Get("id").value] = focus.Get("relative_position_id").value

focus_ord = {}

for focus in root_obj.Get("focus_tree").value:
    if focus.id == "focus":

        val = 0
        id = focus.Get("id").value
        while id in focus_rel:
            id = focus_rel[id]
            val += 1

        focus_ord[focus.Get("id").value] = val

#print(focus_rel)
#print(focus_ord)

def reorder_focus_objects(obj_list, focus_ord):
    # 1. Find the indices of all objects where obj.id == "focus"
    focus_indices = [i for i, obj in enumerate(obj_list) if obj.id == "focus"]
    
    # If there are fewer than 2 "focus" objects, no sorting is needed
    if len(focus_indices) < 2:
        return obj_list
        
    # 2. Extract just the "focus" objects
    focus_objs = [obj_list[i] for i in focus_indices]
    
    # 3. Sort the extracted objects by their priority in focus_ord
    # Since we already filtered for obj.id == "focus", it is safe to call .Get("id")
    focus_objs.sort(key=lambda obj: focus_ord[obj.Get("id").value])
    
    # 4. Place the sorted objects back into their original slots in the main list
    for index, sorted_obj in zip(focus_indices, focus_objs):
        obj_list[index] = sorted_obj
        
    return obj_list

tree = root_obj.Get("focus_tree")
l = tree.value

l = reorder_focus_objects(l, focus_ord)

tree.value = l
SaveObjToFile(tree, filepath)