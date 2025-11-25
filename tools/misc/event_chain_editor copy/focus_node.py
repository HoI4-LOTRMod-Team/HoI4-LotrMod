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


def add_generic_option(node):
    new_option_base_name = node.focus_id
    for l in ['a', 'b', 'c', 'e', 'f', 'g']: # Skipping d because it often designates the description
        if not any(on.option_id == new_option_base_name+"."+l for on in node.options):
            new_option_base_name = new_option_base_name+"."+l
            break
    node.add_option(new_option_base_name)
    node.parent_tree.locfile.add(new_option_base_name, "TODO")

class EventOption:
    option_id = ""
    port = None


class FocusNode(BaseNode):

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node A'


    options = []



    def __init__(self):
        super(FocusNode, self).__init__()

        self.props = [
            StringProperty("Title", attr_name="title"),
            TextProperty("Desc", attr_name="desc"),
            BoolProperty("fire_only_once", attr_name="fire_only_once"),
            BoolProperty("trigger", attr_name="trigger"),
            BoolProperty("is_triggered_only", attr_name="is_triggered_only"),
            BoolProperty("picture", attr_name="picture"),
            ButtonProperty("Add Option", add_generic_option, "Add Option")
        ]

        # create node inputs.
        self.add_input('trigger', multi_input=True)


    # Use this to keep the pObj up to date !
    def __setattr__(self, name, value):

        # Called whenever ANY attribute is set
        if self.is_activated and hasattr(self, name):
            old_value = getattr(self, name)

            if old_value != value:

                if name == "title":
                    self.parent_tree.locfile.set(self.pObj.Get("title").value, value)

                if name == "desc":
                    self.parent_tree.locfile.set(self.pObj.Get("desc").value, value)

                if name == "is_triggered_only":
                    if not self.pObj.Has("is_triggered_only"):
                        self.pObj.InsertAt("is_triggered_only = yes", 4)
                    self.pObj.Get("is_triggered_only").value = "yes" if value else "no"

                if name == "fire_only_once":
                    if not self.pObj.Has("fire_only_once"):
                        self.pObj.InsertAt("fire_only_once = yes", 4)
                    self.pObj.Get("fire_only_once").value = "yes" if value else "no"

                if name == "trigger":
                    if self.pObj.Has("trigger") and not value:
                        self.pObj.Remove("trigger")
                    elif not self.pObj.Has("trigger") and value:
                        self.pObj.InsertAt("trigger = { always = no } # TODO", 4)

                if name == "picture":
                    if self.pObj.Has("picture") and not value:
                        self.pObj.Remove("picture")
                    elif not self.pObj.Has("picture") and value:
                        self.pObj.InsertAt("picture = GFX_report_event_ring # TODO", 4)


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

            option = self.add_option(port_name)
            new_port = option.port

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


    def add_option(self, option_name):
        option = EventOption()
        option.option_id = option_name
        option.port = self.add_output(name=option_name)
        self.options.append(option)
        self.props.append(
            StringProperty(option_name, attr_name=option_name, value_getter=lambda x:x.get_loc(option_name))#,   value_setter=lambda x, v:)) # TODO
        )
        #print(len(self.props))

        return option



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

        self.title = self.get_loc(obj.Get("title").value)
        self.desc = self.get_loc(obj.Get("desc").value)
        if obj.Has("is_triggered_only"):
            self.is_triggered_only = obj.GetVal("is_triggered_only").lower() == "yes"
        if obj.Has("fire_only_once"):
            self.fire_only_once = obj.GetVal("fire_only_once").lower() == "yes"
        self.trigger = obj.Has("trigger")
        self.picture = obj.Has("picture")

        if is_new_focus:
            pass # TODO

    def get_loc(self, loc):
        loc = str(loc)
        ret = self.parent_tree.locfile.get(loc)
        if ret is None:
            return "--invalid--"
        return ret

    def activate(self):
        self.is_activated = True
        

    props = [ ]

    def get_properties(self):
        return self.props

    focus_id = ""

    title = ""
    desc = ""

    fire_only_once = False
    trigger = False
    is_triggered_only = False
    picture = False
    

    parent_tree = None

    is_activated = False


    pObj = None

    




