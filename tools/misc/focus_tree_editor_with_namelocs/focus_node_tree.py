

from pdx_parser import Parse_PObj, Parse_List, PObj, SaveListToFile, ParseListFromFile, ParseListFromFile_asPObj, SaveObjValueToFile

from core import *

from focus_node import FocusNode

from locfile import LocFile


class FocusNodeTree:

    focuses = []

    root_pobj = None

    locfile = None

    def get_focus_node_by_name(self, name):
        for focus in self.focuses:
            if focus.focus_id == name:
                return focus
        return None
    
    def save_focus_tree(self, filepath):
        SaveObjValueToFile(self.root_pobj, filepath)
        self.locfile.save(r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\localisation\english\shire\shire_focus_l_english.yml')
    
    def __init__(self, graph, filepath):

        self.locfile = LocFile(r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\localisation\english\shire\shire_focus_l_english.yml')

        focus_menu = graph.get_context_menu('graph').add_menu('Focus Tree')
        focus_menu.add_command('Save Focus Tree', lambda: self.save_focus_tree(filepath), 'Ctrl+S')

        self.root_pobj = ParseListFromFile_asPObj(filepath)
        if self.root_pobj.Has("focus_tree"):
            focus_list = self.root_pobj.Get("focus_tree")
            focuses_pobjs = focus_list.GetAll("focus").value
        else:
            focuses_pobjs = self.root_pobj.GetAll("shared_focus").value

        # Create a node in the graph for each focus and set the respective values
        for focus in focuses_pobjs:
            focus_1 = graph.create_node('nodes.basic.FocusNode')
            focus_1.init(focus, self)

        # set rel pos
        for focus in self.focuses:
            focus.init_rel_pos_id()

        # post-init function
        for focus in self.focuses:
            focus.post_init()

        # activate
        for focus in self.focuses:
            focus.activate()