

from pdx_parser import *


PATH = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\rhudaur.txt'


focus_tree = ParseObjFromFile(PATH)

focuses = focus_tree.GetAll("focus").value

for focus in focuses:
    if not focus.Has("ai_will_do"):
        focus.Get("cost").InsertAfter("ai_will_do = {\n\t\t\tfactor = 1\n\t\t}")

SaveObjToFile(focus_tree, PATH)


