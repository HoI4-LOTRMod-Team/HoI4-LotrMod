

import signal
from pathlib import Path
import random
import string

from Qt import QtCore, QtWidgets, QtGui

from focus_node import FocusNode
from fake_event_node import FakeFocusNode
from NodeGraphQt import (
    NodeGraph,
    NodesPaletteWidget,
    NodesTreeWidget,
    PropertiesBinWidget,
)
from NodeGraphQt.constants import LayoutDirectionEnum
from NodeGraphQt.constants import PipeLayoutEnum

from pdx_parser import Parse_PObj

BASE_PATH = Path(__file__).parent.resolve()



def add_focus_to_graph(graph):
    focus = graph.create_node('nodes.basic.FocusNode')
    
    focus.init(None, graph.focus_tree)
    focus.post_init()
    focus.activate()

    (x, y) = graph.cursor_pos()
    focus.set_pos(x, y)
    focus.on_node_moved()

    #focus.recalculate_positions()



class FocusNodeGraph(NodeGraph):

    focus_tree = None

    def _on_nodes_moved(self, node_data):
        """
        called when selected nodes in the viewer has changed position.

        Args:
            node_data (dict): {<node_view>: <previous_pos>}
        """

        for node_view, prev_pos in node_data.items():
            node = self._model.nodes[node_view.id]

            # This snaps the nodes in this graph to coordinates that are a multiple of 100
            node.on_node_moved()

        self._undo_stack.endMacro()

        super(FocusNodeGraph, self)._on_nodes_moved(node_data)


def create_node_graph():
    graph = FocusNodeGraph()

    hotkey_path = Path(BASE_PATH, 'hotkeys', 'hotkeys.json')
    graph.set_context_menu_from_file(hotkey_path, 'graph')

    graph.register_nodes([
        FocusNode,
        FakeFocusNode
    ])
        

    focus_menu = graph.get_context_menu('graph').add_menu('Focus')
    focus_menu.add_command('Add Focus', add_focus_to_graph, 'n')


    return graph


def create_main_window():
    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle("Focus Tree Editor")
    main_window.resize(1100, 800)

    return main_window

