

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


def create_properties_panel(main_window, graph, focus_node_tree):
    dock_widget = QtWidgets.QDockWidget("Properties Panel", main_window)

    panel_container = QtWidgets.QWidget()
    form_layout = QtWidgets.QFormLayout(panel_container)
    form_layout.setContentsMargins(10, 10, 10, 10)

    # --- 1. DEFINE WIDGETS AND PROPERTY MAP ---
    
    property_map = []

    # --- Property 1: ID (QLineEdit) ---
    edit_id = QtWidgets.QLineEdit()
    property_map.append({
        'label': "ID:",
        'attr': "focus_id",  # The node attribute (e.g., node.focus_name)
        'widget': edit_id,
        'signal': edit_id.editingFinished, # Signal to connect to
        'get_val': lambda w: w.text(),    # How to get value from widget
        'set_val': lambda w, v: w.setText(v), # How to set value on widget
        'clear_val': lambda w: w.clear(), # How to clear widget for "Mixed"
        'set_placeholder': lambda w, t: w.setPlaceholderText(t) # How to set placeholder
    })

    relpos_id = QtWidgets.QLineEdit()
    property_map.append({
        'label': "RelPosID:",
        'attr': "relative_position_id",  # The node attribute (e.g., node.focus_name)
        'widget': relpos_id,
        'signal': relpos_id.editingFinished, # Signal to connect to
        'get_val': lambda w: focus_node_tree.get_focus_node_by_name(w.text().strip()),    # How to get value from widget
        'set_val': lambda w, v: w.setText(v.focus_id), # How to set value on widget
        'clear_val': lambda w: w.clear(), # How to clear widget for "Mixed"
        'set_placeholder': lambda w, t: w.setPlaceholderText(t) # How to set placeholder
    })

    # --- Property 2: Cost (QSpinBox) ---
    cost = QtWidgets.QSpinBox()
    cost.setRange(-1000, 1000)
    property_map.append({
        'label': "Cost:",
        'attr': "cost",        # The node attribute (e.g., node.cost)
        'widget': cost,
        'signal': cost.valueChanged,
        'get_val': lambda w: w.value(),
        'set_val': lambda w, v: w.setValue(v),
        'clear_val': lambda w: w.clear(),
        'set_placeholder': lambda w, t: w.lineEdit().setPlaceholderText(t)
    })

    is_active_check = QtWidgets.QCheckBox()
    # Enable tri-state to allow for the "Mixed" state
    is_active_check.setTristate(True) 
    
    property_map.append({
        'label': "Is Active:",
        'attr': "is_active",  # The node attribute (e.g., node.is_active)
        'widget': is_active_check,
        'signal': is_active_check.stateChanged, # Use stateChanged
        
        # Get the boolean value
        'get_val': lambda w: w.isChecked(),
        
        # Set the state: Checked or Unchecked
        'set_val': lambda w, v: (
            w.setTristate(False), # A specific value is not tri-state
            w.setCheckState(QtCore.Qt.Checked if v else QtCore.Qt.Unchecked)
        ),
        
        # Clear (for "Mixed"): Set to PartiallyChecked
        'clear_val': lambda w: (
            w.setTristate(True), # Enable tri-state for "Mixed"
            w.setCheckState(QtCore.Qt.PartiallyChecked)
        ),

        # No placeholder for a checkbox, so do nothing
        'set_placeholder': lambda w, t: None 
    })

    search_filters = ["FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_COOPERATIVE"]
    for filter in search_filters:
        filt = QtWidgets.QCheckBox()
        property_map.append({
            'label': filter+":",
            'attr': "cost",        # The node attribute (e.g., node.cost)
            'widget': filt,
            'signal': filt.stateChanged,
            'get_val': lambda w: True,
            'set_val': lambda w, v: w.setChecked(True),
            'clear_val': lambda w: w.setChecked(False),
            'set_placeholder': lambda w, t: w.setChecked(False)
        })

    # --- 2. ADD WIDGETS TO LAYOUT ---
    for prop in property_map:
        form_layout.addRow(prop['label'], prop['widget'])

    dock_widget.setWidget(panel_container)

    # --- 3. REFACTORED FUNCTIONS ---

    def create_update_function(prop_entry):
        """
        Creates and returns a function that updates a
        specific node property from its widget.
        """
        widget = prop_entry['widget']
        attr_name = prop_entry['attr']
        getter = prop_entry['get_val']

        def update_nodes():
            new_value = getter(widget)
            
            selected_nodes = graph.selected_nodes()
            for node in selected_nodes:
                # We only update nodes that are of the correct type
                # AND have the attribute (to be safe).
                if (node.type_ == 'nodes.basic.FocusNode' and
                    hasattr(node, attr_name)):
                    
                    try:
                        setattr(node, attr_name, new_value)
                    except Exception as e:
                        # Log error if setting the node property fails
                        print(f"Error updating node {node.name()}: {e}")
        
        return update_nodes


    def update_panel_from_node():
        """
        Updates the panel based on the current node selection.
        Hides properties if not all selected nodes have them.
        Handles set_val errors.
        """
        selected_nodes = graph.selected_nodes()
        focus_nodes = [n for n in selected_nodes if n.type_ == 'nodes.basic.FocusNode']

        if not focus_nodes:
            # No FocusNodes selected, hide all rows
            for prop in property_map:
                widget = prop['widget']
                # Use form_layout to hide the entire row (label + widget)
                form_layout.setRowVisible(widget, False)
                
                # Block signals while clearing
                widget.blockSignals(True)
                prop['clear_val'](widget)
                widget.blockSignals(False)
        else:
            # At least one FocusNode is selected
            for prop in property_map:
                widget = prop['widget']
                attr_name = prop['attr']

                # --- NEW CHECK 1: Do all nodes have this attribute? ---
                all_nodes_have_attr = True
                for node in focus_nodes:
                    if not hasattr(node, attr_name):
                        all_nodes_have_attr = False
                        break
                
                # Set row visibility based on the check
                form_layout.setRowVisible(widget, all_nodes_have_attr)

                if not all_nodes_have_attr:
                    continue # Skip to the next property, this one is hidden

                # --- All nodes have the attr, proceed as before ---
                all_values = set(getattr(n, attr_name) for n in focus_nodes)
                
                widget.blockSignals(True)
                
                if len(all_values) == 1:
                    # All nodes have the same value
                    value_to_set = all_values.pop()
                    
                    # --- NEW CHECK 2: Handle set_val failures ---
                    try:
                        prop['set_val'](widget, value_to_set)
                        prop['set_placeholder'](widget, "") # Clear placeholder
                    except Exception as e:
                        # set_val failed (e.g., type mismatch)
                        print(f"Warning: Failed to set widget for '{attr_name}'. Error: {e}")
                        prop['clear_val'](widget)
                        prop['set_placeholder'](widget, "N/A (Error)")
                else:
                    # Mixed values
                    prop['clear_val'](widget) # Clear text
                    prop['set_placeholder'](widget, "--- Mixed ---")
                
                widget.blockSignals(False)


    # 4. Add the dock widget to the main window
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)

    # 5. Connect graph selection TO panel
    graph.node_selection_changed.connect(update_panel_from_node)

    # 6. Connect panel edits TO node
    for prop in property_map:
        update_func = create_update_function(prop)
        prop['signal'].connect(update_func)

    # 7. Set the initial state of the panel
    update_panel_from_node()

    return dock_widget