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
        self.add_input('trigger', multi_input=True)


    # Use this to keep the pObj up to date !
    def __setattr__(self, name, value):

        # Called whenever ANY attribute is set
        if self.is_activated and hasattr(self, name):
            old_value = getattr(self, name)

            #if old_value != value:

        super().__setattr__(name, value)


    def on_node_moved(self):
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
        options = self.pObj.GetAll("option")
        
        # Enumerate so we can number the ports (Option 1, Option 2, etc.)
        for index, opt in enumerate(options.value):
            
            # --- CHANGE 1: Create a dynamic output for this specific option ---
            # You can change the naming logic here if 'opt' has a specific name property
            port_name = opt.Get("name").value
            
            # add_output returns the Port object, which we can use to connect later
            new_port = self.add_output(name=port_name)

            child_events = opt.GetAllRecurse("country_event")
            
            for ev in child_events.value:
                # 1. Normalize the Event ID (Your original logic)
                if ev.ValueIsList():
                    event_id = ev.Get("id").value
                else:
                    event_id = ev.value if hasattr(ev, 'value') else ev

                # 2. Try to find an existing Focus Node
                target_node = self.parent_tree.get_focus_node_by_name(event_id)

                # 3. If not found, handle Fake Focus Node (Find or Create)
                if target_node is None:
                    target_node = self.parent_tree.get_fake_focus_node_by_name(event_id)
                    
                    if target_node is None:
                        target_node = self.parent_tree.graph.create_node('nodes.basic.FakeFocusNode')
                        target_node.init(event_id, self.parent_tree)
                        target_node.activate()

                # 4. Connect output
                if target_node:
                    # --- CHANGE 2: Connect the NEW port to the target ---
                    # We use the port object directly to connect to the target's input
                    new_port.connect_to(target_node.input(0))


    def init(self, obj, parent_tree):
        is_new_focus = False

        if obj is None:
            #template = focus_template.replace("$TOKEN$", random_string(6))
            #obj = Parse_PObj(template)[0]
            is_new_focus = True
        self.pObj = obj

        self.parent_tree = parent_tree
        parent_tree.focuses.append(self)

        self.focus_id = obj.GetVal("id")
        self.set_name(self.focus_id)

        if is_new_focus:
            pass # TODO

    def activate(self):
        self.is_activated = True
        

    def get_properties(self):

        return [
            StringProperty("ID", attr_name="focus_id", is_primary=True),
        ]

    focus_id = ""
    

    parent_tree = None

    is_activated = False


    pObj = None

    




