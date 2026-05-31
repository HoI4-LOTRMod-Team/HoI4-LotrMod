from pathlib import Path

from NodeGraphQt import BaseNode

from NodeGraphQt.nodes.base_node import NodeObject


from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem

from NodeGraphQt.widgets.node_widgets import NodeBaseWidget

from PySide6.QtWidgets import QGraphicsTextItem
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from openrouter_api import query_openrouter

from pdx_parser import Parse_PObj
from helpers import get_connected_network_ordered


from Qt import QtWidgets, QtGui, QtCore

import random
import string

from properties_panel import *

BASE_PATH = Path(__file__).parent.parent.resolve()


focus_template = """

# 
country_event = {
    id = $TOKEN$
    title = $TOKEN$.t
    desc = $TOKEN$.desc

    is_triggered_only = yes

    option = {
        ai_chance = {
            base = 1
        }
        name = $TOKEN$.a
    }
}
"""

option_template = """
    option = {
        ai_chance = {
            base = 1
        }
        name = $TOKEN$
    }
"""


ai_fill_single_prompt = """
I'm working on a hoi4 mod that takes place in the LOTR universe and would like your help to write some of the events.
I'm going to give you localization entries on certain events, where the entries are only rough notes/outlines for the content.
You need to give me back the same entries but filled out properly with nice text befitting of a medieval theme.
Don't make it too proseful/fancy. Keep it simple and mostly to-the-point. You don't *have* to rewrite everything, only do so where it makes sense to improve clarity or tone.
Write in a "we/us" perspective from the given POV. You don't need to add introductory lines mentioning the place or POV unless specified otherwise.
Don't give me back anything else. Your response should *only* be the filled out localization entries.

(Note: the event options may have comments with a hashtag saying what event they lead to.)

Here's a simple example:

If I give you this:

lothlorien.67.t:0 "Title"
lothlorien.67.d:0 "An event from the perspective of Lothlorien about how Moria has fallen to orcs and how we may provide them with shelter"
lothlorien.67.a:0 "Accept"
lothlorien.67.b:0 "Decline"

You return me this:

lothlorien.67.t:0 "Moria falls to the orcs"
lothlorien.67.d:0 "After a bitter struggle, the dwarves of Moria have been driven from their kingdom by a ferocious horde of orcs. The law fobidding entry to all dwarves into Lothlórien has been lifted, and we may harbour these dwarves if we wish."
lothlorien.67.a:0 "Provide the surviving dwarves with refuge."
lothlorien.67.b:0 "This is not our concern."

Understood? Great! Here's the entries I need you to fill out:

$ENTRIES_TOKEN$
"""

# for testing
#response = """
#lothlorien.56.t:0 "A Message from the Golden Wood"
#lothlorien.56.d:0 "From the heart of the enchanted forest of Lothlórien comes an emissary bearing a message of goodwill and the promise of strengthened bonds. The Lady Galadriel extends an olive branch, inviting us to foster closer ties and forge a cooperative future. This gesture speaks to the wisdom and foresight of the Elves, offering us a chance to ally with one of Middle-earth's most ancient and powerful realms."
#lothlorien.56.a:0 "Embrace Lothlórien's offer."
#lothlorien.56.b:0 "We shall stand alone in these uncertain times."
#"""


def add_generic_option(node):
    new_option_base_name = node.focus_id
    for l in ['a', 'b', 'c', 'e', 'f', 'g']: # Skipping d because it often designates the description
        if not any(on.option_id == new_option_base_name+"."+l for on in node.options):
            new_option_base_name = new_option_base_name+"."+l
            break
    node.add_option(new_option_base_name)
    node.parent_tree.locfile.add(new_option_base_name, "TODO")


def ai_fill_locs_single(node):
    entries  = node.parent_tree.locfile.get_entry(node.pObj.Get("title").value) + "\n"
    entries += node.parent_tree.locfile.get_entry(node.pObj.Get("desc").value)  + "\n"
    for opt in node.options:
        entries += node.parent_tree.locfile.get_entry(opt.pObj.Get("name").value)  + "\n"
    prompt = ai_fill_single_prompt.replace("$ENTRIES_TOKEN$", entries)

    #print(prompt)

    response = query_openrouter(prompt)

    #print(response)

    node.parent_tree.locfile.load_from_string(response)

    return


def ai_fill_locs_chain(chain_node):
    # collect all nodes connected to this chain, starting at the highest one (if possible)
    node_list = get_connected_network_ordered(chain_node)
    entries = ""
    for node in node_list:
        entries += node.parent_tree.locfile.get_entry(node.pObj.Get("title").value) + "\n"
        entries += node.parent_tree.locfile.get_entry(node.pObj.Get("desc").value)  + "\n"
        for opt in node.options:
            entries += node.parent_tree.locfile.get_entry(opt.pObj.Get("name").value)
            if len(opt.port.connected_ports()) > 0:
                target_ev = opt.port.connected_ports()[0].node().focus_id
                entries += " # leads to " + target_ev
            entries += "\n"

    prompt = ai_fill_single_prompt.replace("$ENTRIES_TOKEN$", entries)

    print(prompt)

    response = query_openrouter(prompt)

    node.parent_tree.locfile.load_from_string(response)

    return


class EventOption:
    option_id = ""
    port = None
    pObj = None
    target = ""


class FocusNode(BaseNode):

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node A'


    options = []



    def __init__(self):
        super(FocusNode, self).__init__()

        self.options = []

        self.props = [
            ButtonProperty("AI Fill (Single)", ai_fill_locs_single, "AI Fill (Single)"),
            ButtonProperty("AI Fill (Chain)", ai_fill_locs_chain, "AI Fill (Chain)"),

            StringProperty("Title", attr_name="title", value_getter=lambda x:x.get_loc(self.pObj.Get("title").value),   value_setter=lambda x, v:x.parent_tree.locfile.set(self.pObj.Get("title").value, v)),
            TextProperty("Desc", attr_name="desc", value_getter=lambda x:x.get_loc(self.pObj.Get("desc").value),   value_setter=lambda x, v:x.parent_tree.locfile.set(self.pObj.Get("desc").value, v)),
            BoolProperty("fire_only_once", attr_name="fire_only_once"),
            BoolProperty("trigger", attr_name="trigger"),
            BoolProperty("is_triggered_only", attr_name="is_triggered_only"),
            BoolProperty("picture", attr_name="picture"),
            ButtonProperty("Add Option", add_generic_option, "Add Option"),
        ]

        # create node inputs.
        self.add_input('trigger', multi_input=True)


    # Use this to keep the pObj up to date !
    def __setattr__(self, name, value):

        # Called whenever ANY attribute is set
        if self.is_activated and hasattr(self, name):
            old_value = getattr(self, name)

            if old_value != value:

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

        # get option object
        option = next(opt for opt in out_port.node().options if opt.port==out_port)

        # Add this event to it
        option.pObj.Insert("country_event = { id = "+self.focus_id+" days = 3 }")

        #print("prerequitites added: " + out_port.node().focus_id)
        return
    


    def on_input_disconnected(self, in_port, out_port):
        if not self.is_activated: return

        # get option
        option = next(opt for opt in out_port.node().options if opt.port==out_port)

        # get the event we just disconnected
        ev = option.pObj.GetAllRecurse("country_event").value[0]
        ev.parent.RemoveAllWhereRecurse(lambda x: x.id == "country_event" and (x.value == self.focus_id or x.Get("id").value == self.focus_id))

        # lazy shit solution: runt his a couple of times to account for nested scopes
        option.pObj.RemoveAllWhereRecurse(lambda x: x.ValueIsList() and len(x.value) < 1)
        option.pObj.RemoveAllWhereRecurse(lambda x: x.ValueIsList() and len(x.value) < 1)
        option.pObj.RemoveAllWhereRecurse(lambda x: x.ValueIsList() and len(x.value) < 1)
        option.pObj.RemoveAllWhereRecurse(lambda x: x.ValueIsList() and len(x.value) < 1)

        option.target = ""

        #print("prerequitites removed!")
        return


    def post_init(self):
        options = self.pObj.GetAll("option")
        
        # Enumerate so we can number the ports (Option 1, Option 2, etc.)
        for index, opt in enumerate(options.value):
            
            # --- CHANGE 1: Create a dynamic output for this specific option ---
            # You can change the naming logic here if 'opt' has a specific name property
            port_name = opt.Get("name").value

            option = self.add_option(port_name, opt)
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
                    if ev.parent.id != "option":
                        option.target = ev.parent.id
                    new_port.connect_to(target_node.input(0))


    def add_option(self, option_name, pObj=None):
        option = EventOption()

        #print(option_name)
        if pObj is None:
            option.pObj = Parse_PObj(option_template.replace("$TOKEN$", option_name))[0]
            self.pObj.value.append(option.pObj)
        else:
            option.pObj = pObj

        option.option_id = option_name
        option.port = self.add_output(name=option_name)
        self.options.append(option)
        self.props.append(
            StringProperty(option_name, attr_name=option_name, value_getter=lambda x:x.get_loc(option_name),   value_setter=lambda x, v:x.parent_tree.locfile.set(option_name, v))
        )
        self.props.append(
            StringProperty(option_name+"__target", attr_name=option_name+"__target", value_getter=lambda x:x.get_target(option),   value_setter=lambda x, v:x.set_target(option, v))
        )
        #print(len(self.props))

        return option



    def init(self, obj, parent_tree):
        is_new_focus = False

        if obj is None:
            new_event_id = parent_tree.namespace_id
            i = 100
            while any(f.focus_id == new_event_id + "."+str(i) for f in parent_tree.focuses): i+=1
            template = focus_template.replace("$TOKEN$", new_event_id+"."+str(i))
            obj = Parse_PObj(template)[0]
            is_new_focus = True
            parent_tree.locfile.add(obj.GetVal("title"), "TODO")
            parent_tree.locfile.add(obj.GetVal("desc"), "TODO")
            parent_tree.locfile.add(obj.Get("option").GetVal("name"), "Accept")

        self.pObj = obj

        self.parent_tree = parent_tree
        parent_tree.focuses.append(self)

        self.focus_id = obj.GetVal("id")
        self.set_name(self.focus_id)

        if obj.Has("is_triggered_only"):
            self.is_triggered_only = obj.GetVal("is_triggered_only").lower() == "yes"
        if obj.Has("fire_only_once"):
            self.fire_only_once = obj.GetVal("fire_only_once").lower() == "yes"
        self.trigger = obj.Has("trigger")
        self.picture = obj.Has("picture")

        if is_new_focus:
            self.parent_tree.root_pobj.value.append(self.pObj)

    def get_loc(self, loc):
        loc = str(loc)
        ret = self.parent_tree.locfile.get(loc)
        if ret is None:
            self.parent_tree.locfile.add(loc, "TODO")
            return "TODO"
        #if ret is None:
        #    return "--invalid--"
        return ret
    
    def get_target(self, option):
        if len(option.port.connected_ports()) < 1:
            return "-- No connection --"
        return option.target
    
    def set_target(self, option, target):
        # get country_event corresponding to this connection
        ev = option.pObj.GetAllRecurse("country_event").value[0]

        # We had a target previously, but now cleared it
        if target == "":
            ev.parent.value.remove(ev) # Remove the ev from previous parent
            option.pObj.RemoveAllWhereRecurse(lambda x: x.ValueIsList() and len(x.value) < 1) # lazy shit way to remove empty scopes
            option.pObj.RemoveAllWhereRecurse(lambda x: x.ValueIsList() and len(x.value) < 1)
            option.pObj.RemoveAllWhereRecurse(lambda x: x.ValueIsList() and len(x.value) < 1)
            option.pObj.RemoveAllWhereRecurse(lambda x: x.ValueIsList() and len(x.value) < 1)
            option.pObj.Insert(str(ev)) # add event back without any target
        # We previously didn't have a target, but have added one now
        elif option.target == "":
            ev.parent.value.remove(ev) # Remove the ev from previous parent
            option.pObj.Insert(target + " = {\n"+str(ev)+"}") # add it with the new target
        # if it doesn't have a target, enclose it in one
        else:
            ev.parent.id = target
        option.target = target
        return

    def activate(self):
        self.is_activated = True
        

    props = [ ]

    def get_properties(self):
        return self.props

    focus_id = ""

    fire_only_once = False
    trigger = False
    is_triggered_only = False
    picture = False
    

    parent_tree = None

    is_activated = False


    pObj = None

    




