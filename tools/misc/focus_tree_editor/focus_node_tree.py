

from pdx_parser import Parse_PObj, Parse_List, PObj, SaveListToFile, ParseListFromFile, ParseListFromFile_asPObj

from core import *

from nodes.focus_node import FocusNode


class FocusNodeTree:

    focuses = []

    def get_focus_node_by_name(self, name):
        for focus in self.focuses:
            if focus.focus_id == name:
                return focus
        return None
    
    def __init__(self, graph):

        focus_list = ParseListFromFile_asPObj(r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\rohan.txt').Get("focus_tree")

        focuses_pobjs = focus_list.GetAll("focus").value

        # Create a node in the graph for each focus and set the respective values
        for focus in focuses_pobjs:
            focus_1 = graph.create_node('nodes.basic.FocusNode')
            focus_1.set_name("")
            focus_1.focus_id = focus.Get("id").value
            focus_1.x = int(focus.GetVal("x"))
            focus_1.y = int(focus.GetVal("y"))
            focus_1.pObj = focus
            self.focuses.append(focus_1)

        # set relative position id to respective focus
        for focus in self.focuses:
            if focus.pObj.Has("relative_position_id"):
                self.get_focus_node_by_name(focus.pObj.Get("id").value).relative_position_id = self.get_focus_node_by_name(focus.pObj.Get("relative_position_id").value)

        # set positions with relative_position_id in mind
        for focus in self.focuses:
            (x, y) = focus.hoi4_get_absolute_pos()
            (x, y) = focus_to_node_pos((x,y))
            focus.set_pos(x, y)

        # Add prerequisite lines/connections
        for focus in self.focuses:
            if(focus.pObj.Has("prerequisite")):
                curr_f = self.get_focus_node_by_name(focus.pObj.Get("id").value)
                preqs = focus.pObj.GetAll("prerequisite")
                
                for preq in preqs.value:
                    preq_focuses = preq.GetAll("focus")
                    for preq_focus in preq_focuses.value:
                        self.get_focus_node_by_name(preq_focus.value).set_output(0, curr_f.input(0))