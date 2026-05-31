from pathlib import Path

from NodeGraphQt import BaseNode

from NodeGraphQt.nodes.base_node import NodeObject


from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem

from NodeGraphQt.widgets.node_widgets import NodeBaseWidget

from PySide6.QtWidgets import QGraphicsTextItem
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from pdx_parser import *


from Qt import QtWidgets, QtGui, QtCore

import random
import string
import re

from properties_panel import *

BASE_PATH = Path(__file__).parent.parent.resolve()


# NOTE: This is in core.py, but getting it imported here is pain and suffering, so copy-pasted
x_scaling = 150
y_scaling = 150
def focus_to_node_pos(pos):
    (x, y) = pos

    return (x*x_scaling, y*y_scaling)

def node_to_focus_pos(pos):
    (x, y) = pos

    return (int(x/x_scaling), int(y/y_scaling))

def random_string(length):
    chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choice(chars) for _ in range(length))


focus_template = """
    focus = {
        id = VAL_$TOKEN$
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

        # Add a label text item inside the node's graphics object
        label = QGraphicsTextItem("", self.view)
        
        # [OPTIONAL] You can set a default font, but setHtml in update_label will override sizes
        font = QFont()
        font.setPointSize(8) # Base size for the ID
        label.setFont(font)
        label.setDefaultTextColor(Qt.gray)
        
        # Position relative to the node
        label.setPos(5, 5)  # (x, y)
        
        # Disable interaction
        label.setTextInteractionFlags(Qt.NoTextInteraction)
        
        # Store a reference if you want to move/update it later
        self._label_item = label


    # Use this to keep the pObj up to date !
    def __setattr__(self, name, value):

        # Called whenever ANY attribute is set
        if self.is_activated and hasattr(self, name):
            old_value = getattr(self, name)

            if old_value != value:

                if name == "cost" and self.pObj.Has("cost"):
                    self.pObj.Get("cost").value = str(value)

                elif name == "filters" and self.pObj.Has("search_filters"):
                    super().__setattr__(name, value)
                    if len(self.filters) < 1:
                        self.pObj.Get("search_filters").value = "{ }"
                    else:
                        self.pObj.Get("search_filters").value = "{ " + " ".join(self.filters) + " }"

                elif name == "relative_position_id":
                    if self.pObj.Has("relative_position_id"):
                        self.pObj.Get("relative_position_id").value = value.focus_id
                    else:
                        self.pObj.InsertAt("relative_position_id = "+str(value.focus_id), 1)
                    super().__setattr__(name, value)
                    self.recalculate_positions()
                    return

                elif name == "x":
                    self.pObj.Get("x").value = str(value)

                elif name == "y":
                    self.pObj.Get("y").value = str(value)

                elif name == "comment":
                    # first check if there already is a comment
                    raw = self.pObj.Get("completion_reward").GetValueString(withBrackets=False)
                    match = re.search(r"#.*", raw)
                    if match and len(self.pObj.Get("completion_reward").value) > 0:
                        raw = re.sub(r"#.*", "# " + value, raw, count=1)
                        self.pObj.Get("completion_reward").value = Parse_List(raw, parent=self.pObj.Get("completion_reward"))
                        #print(self.pObj.Get("completion_reward"))
                    # Otherwise add it as a LooseToken (This is extremely cheaty and will cause problems)
                    else:
                        self.pObj.Get("completion_reward").InsertAt("\n"+tabspace*(self.pObj.Get("completion_reward").level+1)+"token = token", 0)
                        ch = self.pObj.Get("completion_reward").value[0]
                        ch.id = "# " + value
                        ch.operator = ""
                        ch.value = ""
                        ch.post = "\n"+tabspace*(self.pObj.Get("completion_reward").level)
                        print(self.pObj)
                    super().__setattr__(name, value)
                    self.update_label()

                elif name == "focus_id":
                    # first, check if the name exists already and add random chars if it does:
                    for f in self.parent_tree.focuses:
                        if f != self and f.focus_id == value:
                            value = value + "_" + random_string(6)

                    self.pObj.Get("id").value = str(value)
                    for f in self.parent_tree.focuses:
                        # deal with rel-pos-ids
                        if f.relative_position_id == self: f.pObj.Get("relative_position_id").value = str(value)
                        # deal with prerequisites
                        if f.pObj.Has("prerequisite"):
                            for preq in f.pObj.GetAll("prerequisite").value:
                                for pf in preq.value:
                                    if pf.value == old_value: pf.value = value

                    super().__setattr__(name, value)

                    self.update_label()
                    




            print(f"{name} changed from {old_value} → {value}")

        super().__setattr__(name, value)


    def on_node_moved(self):
        # snap position based on scaling
        (x, y) = (self.pos()[0], self.pos()[1])
        new_x = round(x / x_scaling) * x_scaling
        new_y = round(y / y_scaling) * y_scaling

        self.set_pos(new_x, new_y)
        self.recalculate_positions()

    def on_node_moved_bare(self):
        # snap position based on scaling
        (x, y) = (self.pos()[0], self.pos()[1])
        new_x = round(x / x_scaling) * x_scaling
        new_y = round(y / y_scaling) * y_scaling

        self.set_pos(new_x, new_y)


    def on_input_connected(self, in_port, out_port):
        if not self.is_activated: return

        li = self.pObj.LastIndex(lambda x: x.id == "prerequisite") + 1
        self.pObj.InsertAt("prerequisite = { focus = " + out_port.node().focus_id + " }", li)

        #print("prerequitites added: " + out_port.node().focus_id)
        return
    


    def on_input_disconnected(self, in_port, out_port):
        if not self.is_activated: return

        preq_name = out_port.node().focus_id

        self.remove_all_preqs_with_name(preq_name)

        print("prerequitites removed!")
        return

    
    def remove_all_preqs_with_name(self, preq_name):
        # remove all "focus = preq" that are this
        all_preqs = self.pObj.GetAll("prerequisite").value
        for preq in all_preqs:
            preq.RemoveAllWhere(lambda f: f.value == preq_name)

        # remove all empty prerequisites
        self.pObj.RemoveAllWhere(lambda p: p.id == "prerequisite" and len(p.value) < 1)

    def init_rel_pos_id(self):
        # set realtive-position id
        if self.pObj.Has("relative_position_id"):
            self.parent_tree.get_focus_node_by_name(self.pObj.Get("id").value).relative_position_id = self.parent_tree.get_focus_node_by_name(self.pObj.Get("relative_position_id").value)


    def post_init(self):
        # set the position of this node on the graph correctly
        (x, y) = self.hoi4_get_absolute_pos()
        (x, y) = focus_to_node_pos((x,y))
        self.set_pos(x, y)

        # Add prerequisite lines/connections
        if(self.pObj.Has("prerequisite")):
            curr_f = self.parent_tree.get_focus_node_by_name(self.pObj.Get("id").value)
            preqs = self.pObj.GetAll("prerequisite")
            
            for preq in preqs.value:
                preq_focuses = preq.GetAll("focus")
                for preq_focus in preq_focuses.value:
                    #print(preq_focus.value)
                    try:
                        self.parent_tree.get_focus_node_by_name(preq_focus.value).set_output(0, curr_f.input(0))
                    except:
                        print("Could not find preequisite focus: " + preq_focus.value)


    def init(self, obj, parent_tree):
        is_new_focus = False

        if obj is None:
            template = focus_template.replace("$TOKEN$", "new_focus_" + random_string(6))
            obj = Parse_PObj(template, parent=parent_tree.root_pobj.Get("focus_tree"))[0]
            is_new_focus = True
        if isinstance(obj, tuple) :
            (name, comment) = obj
            template = focus_template.replace("$TOKEN$", name)
            obj = Parse_PObj(template, parent=parent_tree.root_pobj.Get("focus_tree"))[0]
            self.comment = comment
            is_new_focus = True
        self.pObj = obj

        self.set_name("")
        self.parent_tree = parent_tree
        parent_tree.focuses.append(self)

        self.focus_id = obj.GetVal("id")
        self.x = int(obj.GetVal("x"))
        self.y = int(obj.GetVal("y"))
        
        if obj.Has("cost"):
            self.og_cost = self.cost = int(obj.GetVal("cost"))

        # parse comment:
        if obj.Has("completion_reward"):
            raw = obj.Get("completion_reward").raw
            match = re.search(r"#.*", raw)
            if match:
                self.comment = match.group(0).lstrip("#").strip()
        
        self.update_label()

        # We do not set relative_position_id here!

        self.filters = []
        if obj.Has("search_filters"):
            for f in obj.GetVal("search_filters"):
                if f.value not in self.filters: self.filters.append(f.value.strip())
        self.og_filters = self.filters.copy()

        if is_new_focus:
            self.parent_tree.root_pobj.Get("focus_tree").value.append(self.pObj)

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

    
    def update_label(self):
        # [CHANGE] Use HTML to format: Bold ID, smaller gray Comment
        # The <br> adds the new lines
        label_text = f'<b>{self.focus_id}</b>'
        if self.comment:
            label_text += f'<br><br><span style="font-size: 6pt; color: #aaaaaa;">{self.comment}</span>'
        
        self._label_item.setHtml(label_text)
        
        # [CHANGE] Set the width of the text item to the node width minus padding
        # This forces the text to wrap/break words if they are too long
        padding = 0
        node_width = self.view.width
        self._label_item.setTextWidth(node_width - padding)
        

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
            StringProperty("Comment", attr_name="comment"),
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
            BoolProperty("FOCUS_FILTER_NECROMANTIC_FORGE",  attr_name="FOCUS_FILTER_NECROMANTIC_FORGE", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_NECROMANTIC_FORGE"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_NECROMANTIC_FORGE")),
            BoolProperty("FOCUS_FILTER_SAURONS_SCHEDULE",  attr_name="FOCUS_FILTER_SAURONS_SCHEDULE", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_SAURONS_SCHEDULE"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_SAURONS_SCHEDULE")),
            BoolProperty("FOCUS_FILTER_CONTEST_FOR_MIRKWOOD",  attr_name="FOCUS_FILTER_CONTEST_FOR_MIRKWOOD", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_CONTEST_FOR_MIRKWOOD"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_CONTEST_FOR_MIRKWOOD")),
            BoolProperty("FOCUS_FILTER_VALES_CONFEDERATION",  attr_name="FOCUS_FILTER_VALES_CONFEDERATION", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_VALES_CONFEDERATION"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_VALES_CONFEDERATION")),
            BoolProperty("FOCUS_FILTER_LIFE_ALONG_THE_ANDUIN",  attr_name="FOCUS_FILTER_LIFE_ALONG_THE_ANDUIN", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_LIFE_ALONG_THE_ANDUIN"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_LIFE_ALONG_THE_ANDUIN")),
            BoolProperty("FOCUS_FILTER_RESTLESS_HUNGER",  attr_name="FOCUS_FILTER_RESTLESS_HUNGER", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_RESTLESS_HUNGER"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_RESTLESS_HUNGER")),
            BoolProperty("FOCUS_FILTER_GUNDABAD_EXPEDITION",  attr_name="FOCUS_FILTER_GUNDABAD_EXPEDITION", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_GUNDABAD_EXPEDITION"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_GUNDABAD_EXPEDITION")),
            BoolProperty("FOCUS_FILTER_RHUN_CIVIL_WAR",  attr_name="FOCUS_FILTER_RHUN_CIVIL_WAR", value_getter=lambda x:filter_getter(x, "FOCUS_FILTER_RHUN_CIVIL_WAR"),   value_setter=lambda x, v:filter_setter(x, v, "FOCUS_FILTER_RHUN_CIVIL_WAR")),
        ]

        
        
    # internal focus info (hoi4-mode)
    x = 0
    y = 0
    relative_position_id = None

    focus_id = ""
    filters = []
    cost = 10

    comment = ""
    

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
    




