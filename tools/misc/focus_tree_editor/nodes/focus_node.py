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

    
    def set_from_pObj(self, obj):
        self.pObj = obj

        self.focus_id = obj.GetVal("id")
        self.x = int(obj.GetVal("x"))
        self.y = int(obj.GetVal("y"))
        
        if obj.Has("cost"):
            self.og_cost = self.cost = int(obj.GetVal("cost"))

        # We do not set relative_position_id here!

        self.filters = []
        if obj.Has("search_filters"):
            for f in obj.GetVal("search_filters"):
                if f.value not in self.filters: self.filters.append(f.value.strip())
            #print(self.focus_id + ": " + str(self.filters))

        #self.filters = ["FOCUS_FILTER_UNALIGNED"]


        


        
        
    # internal focus info (hoi4-mode)
    x = 0
    y = 0
    relative_position_id = None
    focus_id = ""
    filters = []

    cost = 10
    og_cost = 10

    pObj = None

    def hoi4_get_relative_pos(self):
        return (self.x, self.y)
    
    def hoi4_get_absolute_pos(self):
        if self.relative_position_id != None:
            (px, py) = self.relative_position_id.hoi4_get_absolute_pos()
            return (self.x + px, self.y + py)
        return (self.x, self.y)
    
    def has_changed(self):
        return self.cost != self.og_cost
    
    def apply(self):
        if self.has_changed():
            self.pObj.Get("cost").value = str(self.cost)
    




