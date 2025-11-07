

import signal
from pathlib import Path

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

def node_to_focus_pos(pos):
    (x, y) = pos

    return (int(x/x_scaling), int(y/y_scaling))


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

            node.recalculate_positions()

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

    # Example of checkbox property
    #is_active_check = QtWidgets.QCheckBox()
    #is_active_check.setTristate(True) 
    #property_map.append({
    #    'label': "Is Active:",
    #    'attr': "is_active",  # The node attribute (e.g., node.is_active)
    #    'widget': is_active_check,
    #    'signal': is_active_check.stateChanged, # Use stateChanged
    #    
    #    # Get the boolean value
    #    'get_val': lambda w: w.isChecked(),
    #    
    #    # Set the state: Checked or Unchecked
    #    'set_val': lambda w, v: (
    #        w.setTristate(False), # A specific value is not tri-state
    #        w.setCheckState(QtCore.Qt.Checked if v else QtCore.Qt.Unchecked)
    #    ),
    #    
    #    # Clear (for "Mixed"): Set to PartiallyChecked
    #    'clear_val': lambda w: (
    #        w.setTristate(True), # Enable tri-state for "Mixed"
    #        w.setCheckState(QtCore.Qt.PartiallyChecked)
    #    ),
    #    # No placeholder for a checkbox, so do nothing
    #    'set_placeholder': lambda w, t: None 
    #})

    search_filters = [
        "FOCUS_FILTER_UNALIGNED",
        "FOCUS_FILTER_DEFENSE",
        "FOCUS_FILTER_FARMING",
        "FOCUS_FILTER_RING",
        "FOCUS_FILTER_REVOLUTIONARY",
        "FOCUS_FILTER_ELVEN_FACTIONS",
        "FOCUS_FILTER_COOPERATIVE",
        "FOCUS_FILTER_BELLIGERENT",
        "FOCUS_FILTER_DENETHOR_PARANOIA",
        "FOCUS_FILTER_BOP_GRIMA",
        "FOCUS_FILTER_BOP_THEODEN",
        "FOCUS_FILTER_ROH_STATESCRAFT",
        "FOCUS_FILTER_ROH_LORDS",
        "FOCUS_FILTER_POLITICAL",
        "FOCUS_FILTER_INDUSTRY",
        "FOCUS_FILTER_RESEARCH",
        "FOCUS_FILTER_ANNEXATION",
        "FOCUS_FILTER_STABILITY",
        "FOCUS_FILTER_WAR_SUPPORT",
        "FOCUS_FILTER_MANPOWER",
        "FOCUS_FILTER_ARMY_XP",
        "FOCUS_FILTER_NAVY_XP",
        "FOCUS_FILTER_AIR_XP",
    ]
    for filter_name in search_filters:
        filt_check = QtWidgets.QCheckBox()
        filt_check.setTristate(True)
        
        property_map.append({
            'type': 'list_membership', # --- This is the new type
            'label': filter_name + ":",
            'attr': 'filters',           # The name of the list attribute on the node
            'value': filter_name,        # The string value to check for
            'widget': filt_check,
            'signal': filt_check.stateChanged,
            
            # For list membership, get_val/set_val handle check states,
            # not boolean True/False.
            'get_val': lambda w: w.checkState(),
            'set_val': lambda w, state: w.setCheckState(state),
            'clear_val': lambda w: w.setCheckState(QtCore.Qt.PartiallyChecked),
            'set_placeholder': lambda w, t: None,
        })

    # --- 2. ADD WIDGETS TO LAYOUT ---
    for prop in property_map:
        form_layout.addRow(prop['label'], prop['widget'])

    dock_widget.setWidget(panel_container)

    # --- 3. REFACTORED FUNCTIONS ---

    def create_update_function(prop_entry):
        """
        Creates the update function for a widget.
        Now branches logic based on property 'type'.
        """
        prop_type = prop_entry.get('type', 'attribute')
        widget = prop_entry['widget']
        attr_name = prop_entry['attr']

        if prop_type == 'attribute':
            # --- This is the original logic for simple attributes ---
            getter = prop_entry['get_val']

            def update_nodes_attribute():
                new_value = getter(widget)
                selected_nodes = graph.selected_nodes()
                for node in selected_nodes:
                    if (node.type_ == 'nodes.basic.FocusNode' and
                        hasattr(node, attr_name)):
                        try:
                            setattr(node, attr_name, new_value)
                        except Exception as e:
                            print(f"Error updating node {node.name()}: {e}")
            
            return update_nodes_attribute

        elif prop_type == 'list_membership':
            # --- This is the new logic for list membership ---
            value_to_toggle = prop_entry['value'] # e.g., "filter_1"
            getter = prop_entry['get_val']

            def update_nodes_list_membership():
                # Get the new state from the checkbox
                new_state = getter(widget)
                if new_state == QtCore.Qt.PartiallyChecked:
                    # User cannot manually set to "partial",
                    # this only happens on update.
                    # If they click a partial, it becomes checked.
                    return

                should_have = (new_state == QtCore.Qt.Checked)
                
                selected_nodes = graph.selected_nodes()
                for node in selected_nodes:
                    if not (node.type_ == 'nodes.basic.FocusNode' and
                            hasattr(node, attr_name)):
                        continue
                        
                    # Get the current list (or an empty one)
                    current_list = getattr(node, attr_name, [])
                    if not isinstance(current_list, list):
                        current_list = [] # Ensure it's a list

                    # Make a new list to ensure node properties are set
                    new_list = list(current_list)
                    has_value = (value_to_toggle in new_list)

                    if should_have and not has_value:
                        # --- ADD TO LIST ---
                        new_list.append(value_to_toggle)
                        setattr(node, attr_name, new_list)
                    elif not should_have and has_value:
                        # --- REMOVE FROM LIST ---
                        new_list.remove(value_to_toggle)
                        setattr(node, attr_name, new_list)
            
            return update_nodes_list_membership
        
        return lambda: None # Return an empty function if type is unknown


    def update_panel_from_node():
        """
        Updates the panel based on the current node selection.
        Now branches logic based on property 'type'.
        """
        selected_nodes = graph.selected_nodes()
        focus_nodes = [n for n in selected_nodes if n.type_ == 'nodes.basic.FocusNode']

        if not focus_nodes:
            for prop in property_map:
                form_layout.setRowVisible(prop['widget'], False)
                prop['widget'].blockSignals(True)
                prop['clear_val'](prop['widget'])
                prop['widget'].blockSignals(False)
        else:
            for prop in property_map:
                widget = prop['widget']
                attr_name = prop['attr']
                prop_type = prop.get('type', 'attribute')

                # Check if all selected nodes have this attribute
                all_nodes_have_attr = all(hasattr(n, attr_name) for n in focus_nodes)
                form_layout.setRowVisible(widget, all_nodes_have_attr)

                if not all_nodes_have_attr:
                    continue 

                widget.blockSignals(True)

                if prop_type == 'attribute':
                    # --- This is the original logic ---
                    all_values = set(getattr(n, attr_name) for n in focus_nodes)
                    
                    if len(all_values) == 1:
                        value_to_set = all_values.pop()
                        try:
                            prop['set_val'](widget, value_to_set)
                            prop['set_placeholder'](widget, "")
                        except Exception as e:
                            print(f"Warning: Failed to set widget for '{attr_name}'. Error: {e}")
                            prop['clear_val'](widget)
                            prop['set_placeholder'](widget, "N/A (Error)")
                    else:
                        prop['clear_val'](widget)
                        prop['set_placeholder'](widget, "--- Mixed ---")
                
                elif prop_type == 'list_membership':
                    # --- This is the new logic ---
                    value_to_check = prop['value']
                    
                    # Get the "state" (True/False) for this value from every node
                    all_states = set()
                    for node in focus_nodes:
                        current_list = getattr(node, attr_name, [])
                        if not isinstance(current_list, list):
                            current_list = []
                        all_states.add(value_to_check in current_list)
                    
                    if len(all_states) == 1:
                        # All nodes are the same (all have it or all don't)
                        state = all_states.pop()
                        widget.setTristate(False)
                        widget.setCheckState(QtCore.Qt.Checked if state else QtCore.Qt.Unchecked)
                    else:
                        # Mixed (some have it, some don't)
                        widget.setTristate(True)
                        widget.setCheckState(QtCore.Qt.PartiallyChecked)

                widget.blockSignals(False)

    # 4. Add the dock widget to the main window
    main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)

    # 5. Connect graph selection TO panel (Unchanged)
    graph.node_selection_changed.connect(update_panel_from_node)

    # 6. Connect panel edits TO node (Unchanged)
    for prop in property_map:
        update_func = create_update_function(prop)
        prop['signal'].connect(update_func)

    # 7. Set the initial state of the panel (Unchanged)
    update_panel_from_node()

    return dock_widget