from pathlib import Path

from NodeGraphQt import BaseNode

from NodeGraphQt.nodes.base_node import NodeObject


from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem

from NodeGraphQt.widgets.node_widgets import NodeBaseWidget

from PySide6.QtWidgets import QGraphicsTextItem
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


from Qt import QtWidgets, QtGui, QtCore

import random
import string

BASE_PATH = Path(__file__).parent.parent.resolve()


# NOTE: This is in core.py, but getting it imported here is pain and suffering, so copy-pasted
x_scaling = 150
y_scaling = 150
def node_to_tech_pos(pos):
    (x, y) = pos

    return (int(x/x_scaling), int(y/y_scaling))

def random_string(length):
    chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choice(chars) for _ in range(length))


class TechNode(BaseNode):

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node A'



    def __init__(self):
        super(TechNode, self).__init__()

        # create node inputs.
        self.add_input('prerequisites', multi_input=True)

        # create node outputs.
        self.add_output('children')

        self.add_text_input

        # Add a label text item inside the node's graphics object
        label = QGraphicsTextItem("", self.view)
        font = QFont()
        font.setPointSize(8)
        label.setFont(font)
        label.setDefaultTextColor(Qt.gray)
        
        # Position relative to the node
        label.setPos(5, 5)  # (x, y)
        
        # Disable interaction
        label.setTextInteractionFlags(Qt.NoTextInteraction)
        
        # Store a reference if you want to move/update it later
        self._label_item = label



    def __setattr__(self, name, value):

        # Called whenever ANY attribute is set
        if self.is_activated and hasattr(self, name):
            old_value = getattr(self, name)

            #if old_value != value:
                # TODO


            print(f"{name} changed from {old_value} → {value}")

        super().__setattr__(name, value)



    def on_input_connected(self, in_port, out_port):
        if not self.is_activated: return

        li = self.pObj.LastIndex(lambda x: x.id == "path") + 1
        self.pObj.InsertAt("\tpath = { leads_to_tech = " + out_port.node().tech_id + " research_cost_coeff = 1 }", li)

        #print("prerequitites added: " + out_port.node().focus_id)
        return
    


    def on_input_disconnected(self, in_port, out_port):
        if not self.is_activated: return

        preq_name = out_port.node().tech_id

        self.remove_all_preqs_with_name(preq_name)

        #print("prerequitites removed!")
        return

    
    def remove_all_preqs_with_name(self, preq_name):
        # remove all "focus = preq" that are this
        for ch in self.pObj.value:
            if ch.id == "path" and ch.Get("leads_to_tech").value == preq_name:
                self.pObj.value.remove(ch)



    def set_from_pObj(self, obj, is_new_tech=False):
        self.pObj = obj

        self.tech_id = obj.id
        self._label_item.setPlainText(self.tech_id)

        valid_folder = "infantry_folder"

        folder = obj.First(lambda x: x.id=="folder" and x.Get("name").value == valid_folder)
        self.x = int(folder.Get("position").GetVal("x"))
        self.y = int(folder.Get("position").GetVal("y"))
        
        if obj.Has("cost"):
            self.og_cost = self.cost = int(obj.GetVal("cost"))

        if is_new_tech:
            # TODO
            return
            #self.parent_tree.root_pobj.Get("focus_tree").value.append(self.pObj)
        
        
    # internal focus info (hoi4-mode)
    x = 0
    y = 0

    tech_id = ""
    

    parent_tree = None

    is_activated = False


    pObj = None
    




