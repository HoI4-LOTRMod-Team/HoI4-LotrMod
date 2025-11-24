

from pdx_parser import Parse_PObj, Parse_List, PObj, SaveListToFile, ParseListFromFile, ParseListFromFile_asPObj, SaveObjValueToFile

from core import *

from nodes.tech_node import TechNode


class TechNodeTree:

    techs = []

    root_pobj = None

    def get_tech_node_by_name(self, name):
        for tech in self.techs:
            if tech.tech_id == name:
                return tech
        return None
    
    def save_tech_tree(self):
        SaveObjValueToFile(self.root_pobj, r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\technologies\infantry.txt')
    
    def __init__(self, graph):

        tech_menu = graph.get_context_menu('graph').add_menu('Tech Tree')
        tech_menu.add_command('Save Tech Tree', self.save_tech_tree, 'Ctrl+S')

        self.root_pobj = ParseListFromFile_asPObj(r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\technologies\infantry.txt')
        tech_list = self.root_pobj.Get("technologies")

        techs_pobjs = tech_list.value

        # Create a node in the graph for each tech and set the respective values
        for tech in techs_pobjs:
            tech_1 = graph.create_node('nodes.basic.TechNode')
            tech_1.set_from_pObj(tech)
            tech_1.set_name("")
            #tech_1.tech_id = tech.Get("id").value
            #tech_1.x = int(tech.GetVal("x"))
            #tech_1.y = int(tech.GetVal("y"))
            #tech_1.pObj = tech
            self.techs.append(tech_1)

        # set positions with relative_position_id in mind
        for tech in self.techs:
            (x, y) = (tech.x, tech.y)
            (x, y) = tech_to_node_pos((x,y))
            tech.set_pos(x, y)

        # Add prerequisite lines/connections
        # TODO

        for tech in self.techs:
            tech.parent_tree = self
            tech.is_activated = True