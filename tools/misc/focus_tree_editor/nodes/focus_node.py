from pathlib import Path

from NodeGraphQt import BaseNode

from NodeGraphQt.nodes.base_node import NodeObject


from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem

from NodeGraphQt.widgets.node_widgets import NodeBaseWidget



from Qt import QtWidgets, QtGui, QtCore

BASE_PATH = Path(__file__).parent.parent.resolve()




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

        #self.create_property('focus_cost', 5)
        self.create_property('focus_icon', 'GFX_placeholder_icon', tab="properties")
        #self.create_property('focus_relative_position_id', '')


        #self.add_text_input('cost', "5")
        #self.add_text_input('focus_icon', "GFX_placeholder_icon")


        self.add_text_input('my_notes', 'id', text=self.focus_id)
        notes_widget = self.get_widget('my_notes')
        notes_widget.value_changed.connect(self.on_notes_changed)

        # 2. Load the image using QPixmap
        #image_path = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\tools\subscripts\res\leader_frame.png'
        #self.set_icon(image_path)

    def on_notes_changed(self, text, text2):
        """
        This method is a "slot" that runs every time the
        'my_notes' text field signal fires.
        
        The 'text' argument is the new string, passed automatically
        by the textChanged signal.
        """
        # Action 1: Change the node's name to match the text
        focus_id = text2

        
        
    # internal focus info (hoi4-mode)
    x = 0
    y = 0
    relative_position_id = None
    focus_id = ""

    pObj = None

    def hoi4_get_relative_pos(self):
        return (self.x, self.y)
    
    def hoi4_get_absolute_pos(self):
        if self.relative_position_id != None:
            (px, py) = self.relative_position_id.hoi4_get_absolute_pos()
            return (self.x + px, self.y + py)
        return (self.x, self.y)



