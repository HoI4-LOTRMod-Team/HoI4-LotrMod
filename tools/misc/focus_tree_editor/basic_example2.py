#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal
from pathlib import Path

from pdx_parser import Parse_PObj, Parse_List, PObj, SaveListToFile, ParseListFromFile, ParseListFromFile_asPObj

from focus_node_tree import FocusNodeTree

from core import *

from Qt import QtCore, QtWidgets

from nodes import focus_node
from NodeGraphQt import (
    NodeGraph,
    NodesPaletteWidget,
    NodesTreeWidget,
    PropertiesBinWidget,
)
from NodeGraphQt.constants import LayoutDirectionEnum
from NodeGraphQt.constants import PipeLayoutEnum

BASE_PATH = Path(__file__).parent.resolve()



def main():
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication([])

    # create graph controller.
    graph = create_node_graph()

    focus_node_tree = FocusNodeTree(graph)
    graph.focus_tree = focus_node_tree

    context_menu = graph.get_context_menu('graph')
    main_window = create_main_window()
    main_window.setCentralWidget(graph.widget)
    dock_widget = create_properties_panel(main_window, graph, focus_node_tree)



    # Present
    main_window.show()
    graph.clear_selection()
    graph.fit_to_selection()
    graph.set_layout_direction(LayoutDirectionEnum.VERTICAL.value)
    graph.set_pipe_style(PipeLayoutEnum.ANGLE.value)


    # This code-block enables showing a properties widget on double clicking a node
    # create a node properties bin widget.
    #properties_bin = PropertiesBinWidget(node_graph=graph, parent=main_window)
    #properties_bin.setWindowFlags(QtCore.Qt.Tool)
    ## example show the node properties bin widget when a node is double-clicked.
    #def display_properties_bin(node):
    #    if not properties_bin.isVisible():
    #        properties_bin.show()
    ## wire function to "node_double_clicked" signal.
    #graph.node_double_clicked.connect(display_properties_bin)



    # Define your "update" function
    def update():
        if len(graph.selected_nodes()) > 0:
            print(graph.selected_nodes()[0].pos())

    # Use a QTimer to call the update function repeatedly
    timer = QtCore.QTimer()
    #timer.timeout.connect(update) # un-comment this to enable update function
    timer.start(16)  # roughly 60 FPS (1000 ms / 60 ≈ 16 ms)



    app.exec()


if __name__ == '__main__':
    main()
