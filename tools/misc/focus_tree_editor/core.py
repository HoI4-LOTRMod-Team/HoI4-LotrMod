

import signal
from pathlib import Path
import random
import string

from Qt import QtCore, QtWidgets, QtGui

from focus_node import FocusNode
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


class FocusNameDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(FocusNameDialog, self).__init__(parent)
        self.setWindowTitle("Create New Focus")
        self.setMinimumWidth(300)

        # Layouts
        layout = QtWidgets.QVBoxLayout(self)
        form_layout = QtWidgets.QFormLayout()

        # Inputs
        self.id_input = QtWidgets.QLineEdit()
        self.name_input = QtWidgets.QLineEdit()
        
        # Add inputs to form
        form_layout.addRow("Focus ID:", self.id_input)
        form_layout.addRow("Focus Comment:", self.name_input)
        
        layout.addLayout(form_layout)

        # Buttons (OK / Cancel)
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        layout.addWidget(self.buttons)

        # Select the first text field automatically
        self.id_input.setFocus()

    def get_data(self):
        """Return the data entered by the user"""
        return self.id_input.text(), self.name_input.text()


def add_focus_to_graph(graph):
    focus = graph.create_node('nodes.basic.FocusNode')
    
    focus.init(None, graph.focus_tree)
    focus.post_init()
    focus.activate()

    (x, y) = graph.cursor_pos()
    focus.set_pos(x, y)
    focus.on_node_moved()

    focus.recalculate_positions()


def add_named_focus_to_graph(graph):
    # 1. Capture cursor position immediately
    (x, y) = graph.cursor_pos()

    # 2. Open the Dialog
    dialog = FocusNameDialog(parent=graph.widget)
    
    # If user presses OK (or Enter), dialog.exec_() returns True (Accepted)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        focus_name, focus_comment = dialog.get_data()

        # 3. Create the node exactly like the original function
        focus = graph.create_node('nodes.basic.FocusNode')
        
        focus.init((focus_name, focus_comment), graph.focus_tree)
        focus.post_init()
        focus.activate()

        # 4. Set the position
        focus.set_pos(x, y)
        focus.on_node_moved()

        focus.recalculate_positions()



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
                node.on_node_moved_bare()
        for node in self.focus_tree.focuses:
            node.recalculate_positions()


        self._undo_stack.endMacro()

        super(FocusNodeGraph, self)._on_nodes_moved(node_data)

    def delete_nodes(self, nodes, push_undo=True):
        """
        Override the bulk deletion method to inject pre-deletion logic.
        """
        # 1. Safety check (Base class does this, but good to check before iterating)
        if not nodes:
            return

        # 2. RUN YOUR CUSTOM LOGIC HERE
        # The 'nodes' list contains the actual NodeObjects before they are destroyed.
        try:
            for node in nodes:
                print(f"PRE-DELETE: Preparing to delete '{node.name()}' (ID: {node.id})")
                
                node.pObj.parent.value.remove(node.pObj)

        except Exception as e:
            print(f"Error in pre-delete logic: {e}")

        # 3. Call the original implementation to handle the actual removal
        super(FocusNodeGraph, self).delete_nodes(nodes, push_undo)


def create_node_graph():
    graph = FocusNodeGraph()

    hotkey_path = Path(BASE_PATH, 'hotkeys', 'hotkeys.json')
    graph.set_context_menu_from_file(hotkey_path, 'graph')

    graph.register_nodes([
        FocusNode,
    ])
        
    focus_menu = graph.get_context_menu('graph').add_menu('Focus')
    
    # Existing "N" hotkey
    focus_menu.add_command('Add Focus', add_focus_to_graph, 'n')
    
    # --- NEW "M" HOTKEY ---
    focus_menu.add_command('Add Named Focus', add_named_focus_to_graph, 'm')

    return graph


def create_main_window():
    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle("Focus Tree Editor")
    main_window.resize(1100, 800)

    return main_window


def setup_node_count_display(window, graph):
    """
    Adds a node counter to the Main Window status bar and 
    connects it to the graph's signals.
    """
    # 1. Create the label widget
    count_label = QtWidgets.QLabel("Total Nodes: 0")
    # Adding some padding for visual appeal
    count_label.setStyleSheet("padding-right: 10px;") 
    
    # 2. Add it to the window's status bar
    # 'addPermanentWidget' places it on the far right side
    window.statusBar().addPermanentWidget(count_label)

    # 3. Define the update logic
    def update_count(*args):
        # We ignore *args (signal data) and just recount the total
        count = len(graph.all_nodes())
        count_label.setText(f"Total Nodes: {count}")

    # 4. Connect to relevant graph signals
    # Fires when a new node is added (via N, M, or Paste)
    graph.node_created.connect(update_count)
    # Fires when nodes are deleted
    graph.nodes_deleted.connect(update_count)
    
    # 5. Run once immediately to set initial state
    update_count()