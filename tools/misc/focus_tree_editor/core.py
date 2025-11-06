

import signal
from pathlib import Path

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



x_scaling = 150
y_scaling = 150


def snap_node_pos(pos):
    (x, y) = pos

    new_x = round(x / x_scaling) * x_scaling
    new_y = round(y / y_scaling) * y_scaling

    return (new_x, new_y)


def focus_to_node_pos(pos):
    (x, y) = pos

    return (x*x_scaling, y*y_scaling)


def add_focus_to_graph(graph):
    focus = graph.create_node('nodes.basic.FocusNode')
    (x, y) = graph.cursor_pos()
    x = round((x - (0.5*x_scaling)) / x_scaling) * x_scaling
    y = round((y - (0.5*y_scaling)) / y_scaling) * y_scaling
    focus.set_pos(x, y)



class FocusNodeGraph(NodeGraph):

    def _on_nodes_moved(self, node_data):
        """
        called when selected nodes in the viewer has changed position.

        Args:
            node_data (dict): {<node_view>: <previous_pos>}
        """

        for node_view, prev_pos in node_data.items():
            node = self._model.nodes[node_view.id]

            # This snaps the nodes in this graph to coordinates that are a multiple of 100
            (new_x, new_y) = snap_node_pos((node.pos()[0], node.pos()[1]))
            node.set_pos(new_x, new_y)

        self._undo_stack.endMacro()

        super(FocusNodeGraph, self)._on_nodes_moved(node_data)


def create_node_graph():
    graph = FocusNodeGraph()

    hotkey_path = Path(BASE_PATH, 'hotkeys', 'hotkeys.json')
    graph.set_context_menu_from_file(hotkey_path, 'graph')

    graph.register_nodes([
        focus_node.FocusNode,
    ])
        

    focus_menu = graph.get_context_menu('graph').add_menu('Focus')
    focus_menu.add_command('Add Focus', add_focus_to_graph, 'n')


    return graph


def create_main_window():
    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle("NodeGraphQt Example")
    main_window.resize(1100, 800)

    return main_window


def create_properties_panel(main_window, graph):
    dock_widget = QtWidgets.QDockWidget("Properties Panel", main_window)

    panel_container = QtWidgets.QWidget()
    form_layout = QtWidgets.QFormLayout(panel_container)
    form_layout.setContentsMargins(10, 10, 10, 10) # Add padding

    # Create the editable widgets
    # We define them here so our functions below can access them
    edit_id = QtWidgets.QLineEdit()
    edit_x = QtWidgets.QSpinBox()
    edit_y = QtWidgets.QSpinBox()

    # Set ranges for the spin boxes (optional, but good practice)
    edit_x.setRange(-1000, 1000)
    edit_y.setRange(-1000, 1000)

    # Add them to the layout
    form_layout.addRow("ID:", edit_id)
    form_layout.addRow("Grid X:", edit_x)
    form_layout.addRow("Grid Y:", edit_y)
    
    # 5. Add your container widget to the dock widget
    dock_widget.setWidget(panel_container)

    def update_node_from_panel():
        """
        Reads values from the panel and updates the selected node.
        """
        selected_nodes = graph.selected_nodes()
        if not selected_nodes:
            return

        node = selected_nodes[0]
        if node.type_ != 'nodes.basic.FocusNode':
            return

        # Update the node's internal properties from the widgets
        node.focus_name = edit_id.text()
        node.x = edit_x.value()
        node.y = edit_y.value()
        
        # IMPORTANT: Also update the node's visual position in the graph
        # We use the x_scaling/y_scaling from your script's global scope
        node.set_pos(x_scaling * node.x, y_scaling * node.y)

    def update_panel_from_node():
        """
        Reads properties from the selected node and updates the panel.
        """
        selected_nodes = graph.selected_nodes()
        
        # Check if a valid FocusNode is selected
        if selected_nodes and selected_nodes[0].type_ == 'nodes.basic.FocusNode':
            node = selected_nodes[0]
            
            # Block signals from the widgets to prevent a feedback loop
            # (e.g., setValue() firing valueChanged, which calls update_node_from_panel)
            edit_id.blockSignals(True)
            edit_x.blockSignals(True)
            edit_y.blockSignals(True)

            # Update the panel widgets with the node's data
            edit_id.setText(node.focus_name)
            edit_x.setValue(node.x)
            edit_y.setValue(node.y)

            # Re-enable signals
            edit_id.blockSignals(False)
            edit_x.blockSignals(False)
            edit_y.blockSignals(False)
            
            # Enable widgets for editing
            edit_id.setEnabled(True)
            edit_x.setEnabled(True)
            edit_y.setEnabled(True)
            
        else:
            # No node selected, or not a FocusNode. Clear and disable panel.
            edit_id.blockSignals(True)
            edit_x.blockSignals(True)
            edit_y.blockSignals(True)
            
            edit_id.clear()
            edit_x.setValue(0)
            edit_y.setValue(0)
            
            edit_id.blockSignals(False)
            edit_x.blockSignals(False)
            edit_y.blockSignals(False)
            
            edit_id.setEnabled(False)
            edit_x.setEnabled(False)
            edit_y.setEnabled(False)

    # 6. Add the dock widget to the main window
    #    You can change QtCore.Qt.RightDockWidgetArea to .Left, .Top, or .Bottom
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)

    # 7. Connect graph selection TO panel
    graph.node_selection_changed.connect(update_panel_from_node)

    # 8. Connect panel edits TO node
    edit_id.editingFinished.connect(update_node_from_panel)
    edit_x.valueChanged.connect(update_node_from_panel)
    edit_y.valueChanged.connect(update_node_from_panel)

    # 9. Set the initial state of the panel (disabled)
    update_panel_from_node()

    return dock_widget

