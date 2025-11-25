from pathlib import Path

from NodeGraphQt import BaseNodeSVG

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


class FakeFocusNode(BaseNodeSVG):

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node A'



    def __init__(self):
        super(FakeFocusNode, self).__init__()

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
        return
    


    def on_input_disconnected(self, in_port, out_port):
        if not self.is_activated: return
        return


    def post_init(self):
        return


    def init(self, name, parent_tree):

        self.parent_tree = parent_tree
        parent_tree.fake_focuses.append(self)

        self.focus_id = name
        self.set_name(self.focus_id)

    def activate(self):
        self.is_activated = True
        

    def get_properties(self):

        return [
            
        ]

    focus_id = ""
    

    parent_tree = None

    is_activated = False

    




