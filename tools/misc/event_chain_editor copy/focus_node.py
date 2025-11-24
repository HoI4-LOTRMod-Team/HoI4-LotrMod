from pathlib import Path

from NodeGraphQt import BaseNode

from NodeGraphQt.nodes.base_node import NodeObject


from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem

from NodeGraphQt.widgets.node_widgets import NodeBaseWidget

from PySide6.QtWidgets import QGraphicsTextItem
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from pdx_parser import Parse_PObj


from Qt import QtWidgets, QtGui, QtCore

import random
import string

from properties_panel import *

BASE_PATH = Path(__file__).parent.parent.resolve()


focus_template = """
    focus = {
		id = ROH_new_focus_$TOKEN$
		icon = GFX_unknown_focus
		
		x = 0
		y = 0

		cost = 5
		ai_will_do = { factor = 1 }
		
		search_filters = { }
		available = {
			always = yes
		}
		completion_reward = {
			# TODO
		}
	}
"""


class FocusNode(BaseNode):

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node A'



    def __init__(self):
        super(FocusNode, self).__init__()

        # create node inputs.
        self.add_input('prerequisites', multi_input=True)

        # create node outputs.
        self.add_output('children')


    # Use this to keep the pObj up to date !
    def __setattr__(self, name, value):

        # Called whenever ANY attribute is set
        if self.is_activated and hasattr(self, name):
            old_value = getattr(self, name)

            #if old_value != value:

        super().__setattr__(name, value)


    def on_node_moved(self):
        # snap position based on scaling
        return



    def on_input_connected(self, in_port, out_port):
        if not self.is_activated: return

        # TODO

        #print("prerequitites added: " + out_port.node().focus_id)
        return
    


    def on_input_disconnected(self, in_port, out_port):
        if not self.is_activated: return

        # TODO

        #print("prerequitites removed!")
        return


    def post_init(self):
        # TODO

        return


    def init(self, obj, parent_tree):
        is_new_focus = False

        if obj is None:
            #template = focus_template.replace("$TOKEN$", random_string(6))
            #obj = Parse_PObj(template)[0]
            is_new_focus = True
        self.pObj = obj

        self.set_name("")
        self.parent_tree = parent_tree
        parent_tree.focuses.append(self)

        self.focus_id = obj.GetVal("id")

        # We do not set relative_position_id here!

        self.filters = []
        if obj.Has("search_filters"):
            for f in obj.GetVal("search_filters"):
                if f.value not in self.filters: self.filters.append(f.value.strip())
        self.og_filters = self.filters.copy()

        if is_new_focus:
            pass # TODO

    def activate(self):
        self.is_activated = True

    
    def recalculate_positions(self):
        #(ax, ay) = self.hoi4_get_absolute_pos()
        (nx, ny) = node_to_focus_pos(self.pos())
        
        if self.relative_position_id != None:
            (px, py) = self.relative_position_id.hoi4_get_absolute_pos()
            self.x = nx - px
            self.y = ny - py
        else:
            self.x = nx
            self.y = ny
        

    def get_properties(self):
        def rel_pos_getter(node):
            if node.relative_position_id:
                return node.relative_position_id.focus_id
            return ""

        def rel_pos_setter(node, value_str):
            node.relative_position_id = node.parent_tree.get_focus_node_by_name(value_str.strip())

        def filter_getter(node, filter):
            return filter in node.filters
        
        def filter_setter(node, bool_val, filter):
            new_filters = list(node.filters)
            if bool_val: new_filters.append(filter)
            else: new_filters.remove(filter)
            node.filters = new_filters # ensure we trigger setattr


        return [
            StringProperty("ID", attr_name="focus_id", is_primary=True),
            StringProperty(
                "RelPosID", attr_name="relative_position_id", value_getter=rel_pos_getter, value_setter=rel_pos_setter, placeholder="Enter Target ID..."
            ),
            IntProperty("Cost", attr_name="cost"),
            BoolProperty("FOCUS_FILTER_UNALIGNED",  attr_name="FOCUS_FILTER_UNALIGNED", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_UNALIGNED"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_UNALIGNED")),
            BoolProperty("FOCUS_FILTER_DEFENSE",  attr_name="FOCUS_FILTER_DEFENSE", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_DEFENSE"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_DEFENSE")),
            BoolProperty("FOCUS_FILTER_FARMING",  attr_name="FOCUS_FILTER_FARMING", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_FARMING"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_FARMING")),
            BoolProperty("FOCUS_FILTER_RING",  attr_name="FOCUS_FILTER_RING", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_RING"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_RING")),
            BoolProperty("FOCUS_FILTER_REVOLUTIONARY",  attr_name="FOCUS_FILTER_REVOLUTIONARY", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_REVOLUTIONARY"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_REVOLUTIONARY")),
            BoolProperty("FOCUS_FILTER_ELVEN_FACTIONS",  attr_name="FOCUS_FILTER_ELVEN_FACTIONS", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_ELVEN_FACTIONS"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_ELVEN_FACTIONS")),
            BoolProperty("FOCUS_FILTER_COOPERATIVE",  attr_name="FOCUS_FILTER_COOPERATIVE", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_COOPERATIVE"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_COOPERATIVE")),
            BoolProperty("FOCUS_FILTER_BELLIGERENT",  attr_name="FOCUS_FILTER_BELLIGERENT", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_BELLIGERENT"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_BELLIGERENT")),
            BoolProperty("FOCUS_FILTER_DENETHOR_PARANOIA",  attr_name="FOCUS_FILTER_DENETHOR_PARANOIA", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_DENETHOR_PARANOIA"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_DENETHOR_PARANOIA")),
            BoolProperty("FOCUS_FILTER_BOP_GRIMA",  attr_name="FOCUS_FILTER_BOP_GRIMA", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_BOP_GRIMA"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_BOP_GRIMA")),
            BoolProperty("FOCUS_FILTER_BOP_THEODEN",  attr_name="FOCUS_FILTER_BOP_THEODEN", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_BOP_THEODEN"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_BOP_THEODEN")),
            BoolProperty("FOCUS_FILTER_ROH_STATESCRAFT",  attr_name="FOCUS_FILTER_ROH_STATESCRAFT", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_ROH_STATESCRAFT"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_ROH_STATESCRAFT")),
            BoolProperty("FOCUS_FILTER_ROH_LORDS",  attr_name="FOCUS_FILTER_ROH_LORDS", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_ROH_LORDS"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_ROH_LORDS")),
            BoolProperty("FOCUS_FILTER_POLITICAL",  attr_name="FOCUS_FILTER_POLITICAL", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_POLITICAL"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_POLITICAL")),
            BoolProperty("FOCUS_FILTER_INDUSTRY",  attr_name="FOCUS_FILTER_INDUSTRY", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_INDUSTRY"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_INDUSTRY")),
            BoolProperty("FOCUS_FILTER_RESEARCH",  attr_name="FOCUS_FILTER_RESEARCH", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_RESEARCH"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_RESEARCH")),
            BoolProperty("FOCUS_FILTER_ANNEXATION",  attr_name="FOCUS_FILTER_ANNEXATION", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_ANNEXATION"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_ANNEXATION")),
            BoolProperty("FOCUS_FILTER_STABILITY",  attr_name="FOCUS_FILTER_STABILITY", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_STABILITY"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_STABILITY")),
            BoolProperty("FOCUS_FILTER_WAR_SUPPORT",  attr_name="FOCUS_FILTER_WAR_SUPPORT", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_WAR_SUPPORT"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_WAR_SUPPORT")),
            BoolProperty("FOCUS_FILTER_MANPOWER",  attr_name="FOCUS_FILTER_MANPOWER", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_MANPOWER"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_MANPOWER")),
            BoolProperty("FOCUS_FILTER_ARMY_XP",  attr_name="FOCUS_FILTER_ARMY_XP", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_ARMY_XP"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_ARMY_XP")),
            BoolProperty("FOCUS_FILTER_NAVY_XP",  attr_name="FOCUS_FILTER_NAVY_XP", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_NAVY_XP"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_NAVY_XP")),
            BoolProperty("FOCUS_FILTER_AIR_XP",  attr_name="FOCUS_FILTER_AIR_XP", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_AIR_XP"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_AIR_XP")),
        ]

        
        
    # internal focus info (hoi4-mode)
    x = 0
    y = 0
    relative_position_id = None

    focus_id = ""
    filters = []
    cost = 10
    

    parent_tree = None

    is_activated = False


    pObj = None

    def hoi4_get_relative_pos(self):
        return (self.x, self.y)
    
    def hoi4_get_absolute_pos(self):
        if self.relative_position_id != None:
            (px, py) = self.relative_position_id.hoi4_get_absolute_pos()
            return (self.x + px, self.y + py)
        return (self.x, self.y)
    




