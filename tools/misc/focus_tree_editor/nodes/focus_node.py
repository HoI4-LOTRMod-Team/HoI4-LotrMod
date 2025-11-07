from pathlib import Path

from NodeGraphQt import BaseNode

from NodeGraphQt.nodes.base_node import NodeObject


from NodeGraphQt.qgraphics.node_abstract import AbstractNodeItem

from NodeGraphQt.widgets.node_widgets import NodeBaseWidget


from Qt import QtWidgets, QtGui, QtCore

BASE_PATH = Path(__file__).parent.parent.resolve()


# NOTE: This is in core.py, but getting it imported here is pain and suffering, so copy-pasted
x_scaling = 150
y_scaling = 150
def node_to_focus_pos(pos):
    (x, y) = pos

    return (int(x/x_scaling), int(y/y_scaling))


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



    def __setattr__(self, name, value):

        # Called whenever ANY attribute is set
        if self.is_activated and hasattr(self, name):
            old_value = getattr(self, name)

            if old_value != value:

                if name == "cost" and self.pObj.Has("cost"):
                    self.pObj.Get("cost").value = str(value)

                elif name == "filters" and self.pObj.Has("search_filters"):
                    self.pObj.Get("search_filters").value = "{ " + " ".join(self.filters) + " }"

                elif name == "relative_position_id" and self.pObj.Has("relative_position_id"):
                    self.pObj.Get("relative_position_id").value = value.focus_id
                    super().__setattr__(name, value)
                    self.recalculate_positions()
                    return

                elif name == "x":
                    self.pObj.Get("x").value = str(value)

                elif name == "y":
                    self.pObj.Get("y").value = str(value)

                elif name == "focus_id":
                    self.pObj.Get("id").value = str(value)
                    for f in self.parent_tree.focuses:
                        # deal with rel-pos-ids
                        if f.relative_position_id == self: f.pObj.Get("relative_position_id").value = str(value)
                        # deal with prerequisites
                        if f.pObj.Has("prerequisite"):
                            for preq in f.pObj.GetAll("prerequisite").value:
                                for pf in preq.value:
                                    if pf.value == old_value: pf.value = value
                    




            print(f"{name} changed from {old_value} → {value}")

        super().__setattr__(name, value)



    def on_input_connected(self, in_port, out_port):
        if not self.is_activated: return

        li = self.pObj.LastIndex(lambda x: x.id == "prerequisite") + 1
        self.pObj.InsertAt("prerequisite = { focus = " + out_port.node().focus_id + " }", li)

        #print("prerequitites added: " + out_port.node().focus_id)
        return
    


    def on_input_disconnected(self, in_port, out_port):
        if not self.is_activated: return

        preq_name = out_port.node().focus_id

        self.remve_all_preqs_with_name(preq_name)

        #print("prerequitites removed!")
        return

    
    def remve_all_preqs_with_name(self, preq_name):
        # remove all "focus = preq" that are this
        all_preqs = self.pObj.GetAll("prerequisite").value
        for preq in all_preqs:
            preq.RemoveAllWhere(lambda f: f.value == preq_name)

        # remove all empty prerequisites
        self.pObj.RemoveAllWhere(lambda p: p.id == "prerequisite" and len(p.value) < 1)



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
        self.og_filters = self.filters.copy()

    
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
        


        
        
    # internal focus info (hoi4-mode)
    x = 0
    y = 0
    relative_position_id = None

    focus_id = ""
    filters = []
    cost = 10
    

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
    
    def apply(self):
        return
    




