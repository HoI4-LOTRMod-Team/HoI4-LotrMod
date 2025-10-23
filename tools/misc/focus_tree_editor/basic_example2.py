#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal
from pathlib import Path

from pdx_parser import Parse_PObj, Parse_List, PObj, SaveListToFile, ParseListFromFile, ParseListFromFile_asPObj

from Qt import QtCore, QtWidgets

from nodes import focus_node
from nodes import test_image_node
from NodeGraphQt import (
    NodeGraph,
    NodesPaletteWidget,
    NodesTreeWidget,
    PropertiesBinWidget,
)
from NodeGraphQt.constants import LayoutDirectionEnum
from NodeGraphQt.constants import PipeLayoutEnum

BASE_PATH = Path(__file__).parent.resolve()


class FocusNodeGraph(NodeGraph):
    def _on_nodes_moved(self, node_data):
        """
        called when selected nodes in the viewer has changed position.

        Args:
            node_data (dict): {<node_view>: <previous_pos>}
        """
        print("Hiii11111123123")

        for node_view, prev_pos in node_data.items():
            node = self._model.nodes[node_view.id]

            # This snaps the nodes in this graph to coordinates that are a multiple of 100
            new_x = round(node.pos()[0] / 100) * 100
            new_y = round(node.pos()[1] / 100) * 100

            #print(node.pos())
            node.set_pos(new_x, new_y)

        self._undo_stack.endMacro()

        super(FocusNodeGraph, self)._on_nodes_moved(node_data)



def main():
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication([])

    # create graph controller.
    graph = FocusNodeGraph()

    # set up context menu for the node graph.
    hotkey_path = Path(BASE_PATH, 'hotkeys', 'hotkeys.json')
    graph.set_context_menu_from_file(hotkey_path, 'graph')

    # registered example nodes.
    graph.register_nodes([
        focus_node.FocusNode,
        test_image_node.ImageNode
    ])

    # show the node graph widget.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    graph_widget.setWindowTitle("NodeGraphQt Example")
    graph_widget.show()


    focus_list = ParseListFromFile_asPObj(r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\angmar.txt').Get("focus_tree")

    focuses = focus_list.GetAll("focus").value
    #print(focus_list.GetAll("focus"))
    #print(len(focuses))

    graph_focuses = []

    for focus in focuses:
        #print((200*int(focus.GetVal("x")), 200*int(focus.GetVal("y"))))
        #FocusVisual(texture_id, (800+100*int(focus.GetVal("x")), 100*int(focus.GetVal("y"))), focus.Get("id").value)
        focus_1 = graph.create_node('nodes.basic.FocusNode')
        focus_1.set_name(focus.Get("id").value)
        focus_1.x = int(focus.GetVal("x"))
        focus_1.y = int(focus.GetVal("y"))
        graph_focuses.append(focus_1)
        #if focus.Has("relative_position_id"):
        #    focus_1.
        #focus_1.set_pos(
        #    x=100*int(focus.GetVal("x")),
        #    y=100*int(focus.GetVal("y")))
        #focus_1.set_layout_direction(1)

    for focus in focuses:
        if focus.Has("relative_position_id"):
            #print(focus.Get("id").value  + "--->" + focus.Get("relative_position_id").value)
            graph.get_node_by_name(focus.Get("id").value).relative_position_id = graph.get_node_by_name(focus.Get("relative_position_id").value)

    for focus in graph_focuses:
        (x, y) = focus.hoi4_get_absolute_pos()
        print((x, y))
        focus.set_pos(
            100 * x,
            100 * y
        )

    

    #graph.get_node_by_name()
    for focus in focuses:
        if(focus.Has("prerequisite")):
            curr_f = graph.get_node_by_name(focus.Get("id").value)
            preqs = focus.GetAll("prerequisite")
            
            for preq in preqs.value:
                #print(preq)
                preq_focuses = preq.GetAll("focus")
                for preq_focus in preq_focuses.value:
                    print(preq_focus.value)
                    graph.get_node_by_name(preq_focus.value).set_output(0, curr_f.input(0))

    #focus_1 = graph.create_node('nodes.basic.FocusNode')
    #focus_1.set_layout_direction(1)

    node = graph.create_node('nodes.basic.ImageNode')
    node.set_image(r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\tools\subscripts\res\leader_frame.png')

    

    # auto layout nodes.
    #graph.auto_layout_nodes()

    # fit nodes to the viewer.
    graph.clear_selection()
    graph.fit_to_selection()
    graph.set_layout_direction(LayoutDirectionEnum.VERTICAL.value)
    graph.set_pipe_style(PipeLayoutEnum.ANGLE.value)
    #graph.

    # adjust layout of node to be vertical (for all nodes).
    # graph.set_layout_direction(LayoutDirectionEnum.VERTICAL.value)

    # Custom builtin widgets from NodeGraphQt
    # ---------------------------------------

    # create a node properties bin widget.
    properties_bin = PropertiesBinWidget(node_graph=graph, parent=graph_widget)
    properties_bin.setWindowFlags(QtCore.Qt.Tool)

    # example show the node properties bin widget when a node is double-clicked.
    def display_properties_bin(node):
        if not properties_bin.isVisible():
            properties_bin.show()

    # wire function to "node_double_clicked" signal.
    graph.node_double_clicked.connect(display_properties_bin)

    # create a nodes tree widget.
    nodes_tree = NodesTreeWidget(node_graph=graph)
    nodes_tree.set_category_label('nodeGraphQt.nodes', 'Builtin Nodes')
    nodes_tree.set_category_label('nodes.custom.ports', 'Custom Port Nodes')
    nodes_tree.set_category_label('nodes.widget', 'Widget Nodes')
    nodes_tree.set_category_label('nodes.basic', 'Basic Nodes')
    nodes_tree.set_category_label('nodes.group', 'Group Nodes')
    # nodes_tree.show()

    # create a node palette widget.
    nodes_palette = NodesPaletteWidget(node_graph=graph)
    nodes_palette.set_category_label('nodeGraphQt.nodes', 'Builtin Nodes')
    nodes_palette.set_category_label('nodes.custom.ports', 'Custom Port Nodes')
    nodes_palette.set_category_label('nodes.widget', 'Widget Nodes')
    nodes_palette.set_category_label('nodes.basic', 'Basic Nodes')
    nodes_palette.set_category_label('nodes.group', 'Group Nodes')
    # nodes_palette.show()

    #graph._on_nodes_moved

    # Define your "update" function
    def update():
        if len(graph.selected_nodes()) > 0:
            print(graph.selected_nodes()[0].pos())
        #print("Updating...")  # Replace with your per-frame code
        # You can also interact with the NodeGraph here

    #graph._on_nodes_moved

    # Use a QTimer to call the update function repeatedly
    timer = QtCore.QTimer()
    #timer.timeout.connect(update)
    timer.start(16)  # roughly 60 FPS (1000 ms / 60 ≈ 16 ms)

    app.exec()


if __name__ == '__main__':
    main()
