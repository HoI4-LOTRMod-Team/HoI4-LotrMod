from pathlib import Path

from NodeGraphQt import BaseNode

from NodeGraphQt.nodes.base_node import NodeObject


from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem

from NodeGraphQt.widgets.node_widgets import NodeBaseWidget



from Qt import QtWidgets, QtGui, QtCore

GRID_SIZE = 100

BASE_PATH = Path(__file__).parent.parent.resolve()




class FocusNode(BaseNode):
    """
    A node class with 2 inputs and 2 outputs.
    """

    # unique node identifier.
    __identifier__ = 'nodes.basic'

    # initial default node name.
    NODE_NAME = 'node A'

    

    # internal focus info (hoi4-mode)
    x = 0
    y = 0
    relative_position_id = None



    def __init__(self):
        super(FocusNode, self).__init__()

        # create node inputs.
        self.add_input('prerequisites', multi_input=True)

        # create node outputs.
        self.add_output('children')

        # 2. Load the image using QPixmap
        image_path = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\tools\subscripts\res\leader_frame.png'
        self.set_icon(image_path)

        
        


    def hoi4_get_relative_pos(self):
        return (self.x, self.y)
    
    def hoi4_get_absolute_pos(self):
        if self.relative_position_id != None:
            (px, py) = self.relative_position_id.hoi4_get_absolute_pos()
            return (self.x + px, self.y + py)
        return (self.x, self.y)



