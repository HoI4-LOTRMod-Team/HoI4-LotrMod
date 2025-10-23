from NodeGraphQt import BaseNode
from PySide6 import QtCore, QtGui, QtWidgets


class ImageNode(BaseNode):
    """
    A custom node that displays an image centered in the node body.
    """
    __identifier__ = 'nodes.basic'
    NODE_NAME = 'Image Node'

    def __init__(self):
        super().__init__()
        self.image_path = None
        self.image = None

        path = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\tools\subscripts\res\leader_frame.png'
        self.image_path = path
        self.image = QtGui.QPixmap(path)

    def set_image(self, path):
        """Set the image from file path."""
        

        widget = QtWidgets.QLabel("hi there")
        #self.add_custom_widget(widget)
        #self.add_

