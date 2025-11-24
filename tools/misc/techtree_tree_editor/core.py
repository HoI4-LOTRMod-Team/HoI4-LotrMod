

import signal
from pathlib import Path
import random
import string

from Qt import QtCore, QtWidgets, QtGui

from nodes import tech_node
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



x_scaling = 150
y_scaling = 150


def snap_node_pos(pos):
    (x, y) = pos

    new_x = round(x / x_scaling) * x_scaling
    new_y = round(y / y_scaling) * y_scaling

    return (new_x, new_y)


def tech_to_node_pos(pos):
    (x, y) = pos

    return (x*x_scaling, y*y_scaling)

def node_to_tech_pos(pos):
    (x, y) = pos

    return (int(x/x_scaling), int(y/y_scaling))


def random_string(length):
    chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choice(chars) for _ in range(length))


tech_template = """
    tech = {
		id = ROH_new_tech_$TOKEN$
		icon = GFX_unknown_tech
		
		x = 0
		y = 0

		cost = 5
		ai_will_do = { factor = 1 }
		
		search_filters = { }
		available = {
			always = yes
		}
		completion_reward = {
			# TODO
		}
	}
"""


def add_tech_to_graph(graph):
    # TODO
    return
    #tech = graph.create_node('nodes.basic.FocusNode')
    #(x, y) = graph.cursor_pos()
    #x = round((x - (0.5*x_scaling)) / x_scaling) * x_scaling
    #y = round((y - (0.5*y_scaling)) / y_scaling) * y_scaling
    #tech.set_pos(x, y)
    #tech.set_name("")
#
    #graph.tech_tree.teches.append(tech)
#
    #template = tech_template.replace("$TOKEN$", random_string(6))
    #
    #tech.parent_tree = graph.tech_tree
    #tech.set_from_pObj(Parse_PObj(template)[0], True)
    #tech.is_activated = True
    #tech.recalculate_positions()



class TechNodeGraph(NodeGraph):

    tech_tree = None

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

        super(TechNodeGraph, self)._on_nodes_moved(node_data)


def create_node_graph():
    graph = TechNodeGraph()

    hotkey_path = Path(BASE_PATH, 'hotkeys', 'hotkeys.json')
    graph.set_context_menu_from_file(hotkey_path, 'graph')

    graph.register_nodes([
        tech_node.TechNode,
    ])
        

    tech_menu = graph.get_context_menu('graph').add_menu('Tech')
    tech_menu.add_command('Add Tech', add_tech_to_graph, 'n')


    return graph


def create_main_window():
    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle("Tech Tree Editor")
    main_window.resize(1100, 800)

    return main_window


def create_properties_panel(main_window, graph, tech_node_tree):
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
        'attr': "tech_id",  # The node attribute (e.g., node.tech_name)
        'widget': edit_id,
        'signal': edit_id.editingFinished, # Signal to connect to
        'get_val': lambda w: w.text(),    # How to get value from widget
        'set_val': lambda w, v: w.setText(v), # How to set value on widget
        'clear_val': lambda w: w.clear(), # How to clear widget for "Mixed"
        'set_placeholder': lambda w, t: w.setPlaceholderText(t) # How to set placeholder
    })

    # This makes it so we can quick-edit tech names with enter
    shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), main_window)
    def tech_line_edit_if_unteched():
        if not edit_id.hasFocus():
            dock_widget.activateWindow()
            edit_id.setFocus()
            edit_id.selectAll()
        else:
            edit_id.clearFocus()
    shortcut.activated.connect(tech_line_edit_if_unteched)


    # TODO

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
        tech_nodes = [n for n in selected_nodes if n.type_ == 'nodes.basic.FocusNode']

        if not tech_nodes:
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
                all_nodes_have_attr = all(hasattr(n, attr_name) for n in tech_nodes)
                form_layout.setRowVisible(widget, all_nodes_have_attr)

                if not all_nodes_have_attr:
                    continue 

                widget.blockSignals(True)

                if prop_type == 'attribute':
                    # --- This is the original logic ---
                    all_values = set(getattr(n, attr_name) for n in tech_nodes)
                    
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
                    for node in tech_nodes:
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