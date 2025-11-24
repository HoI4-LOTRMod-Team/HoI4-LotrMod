

from Qt import QtWidgets, QtCore, QtGui


class NodeProperty:
    def __init__(self, label, attr_name=None, value_getter=None, value_setter=None, is_primary=False):
        self.label = label
        self.attr_name = attr_name
        self._getter = value_getter
        self._setter = value_setter
        self.is_primary = is_primary

    def get_value(self, node):
        """Helper to get value from a node, using custom logic or default attribute."""
        if self._getter:
            return self._getter(node)
        return getattr(node, self.attr_name)

    def set_value(self, node, value):
        """Helper to set value on a node, using custom logic or default attribute."""
        if self._setter:
            self._setter(node, value)
        else:
            setattr(node, self.attr_name, value)

class StringProperty(NodeProperty):
    def __init__(self, label, attr_name, placeholder="", **kwargs):
        super().__init__(label, attr_name, **kwargs)
        self.placeholder = placeholder

class IntProperty(NodeProperty):
    def __init__(self, label, attr_name, min_val=-1000, max_val=1000, **kwargs):
        super().__init__(label, attr_name, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

class BoolProperty(NodeProperty):
    def __init__(self, label, attr_name, **kwargs):
        # kwargs allows passing value_getter / value_setter up to NodeProperty
        super().__init__(label, attr_name, **kwargs)




class PropertiesPanel(QtWidgets.QDockWidget):
    def __init__(self, main_window, graph):
        super().__init__("Properties Panel", main_window)
        self.graph = graph
        
        # Main Container
        self.container = QtWidgets.QWidget()
        self.form_layout = QtWidgets.QFormLayout(self.container)
        self.form_layout.setContentsMargins(10, 10, 10, 10)
        self.setWidget(self.container)

        # Store active widget references to block signals during updates
        self._active_widgets = [] 

        # Connect Graph Signals
        # Assuming graph has a signal: node_selection_changed
        self.graph.node_selection_changed.connect(self.refresh_panel)

        # 1. Store a reference to the current "Quick Edit" widget
        self._primary_widget = None

        # 2. Setup the Shortcut (Global context)
        self.shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), main_window)
        self.shortcut.activated.connect(self._on_quick_edit_shortcut)

    def refresh_panel(self):
        self._clear_layout()
        self._active_widgets = []
        
        # Reset the primary widget reference on every refresh
        self._primary_widget = None 

        selected_nodes = self.graph.selected_nodes()
        if not selected_nodes: return

        common_props = self._get_common_properties(selected_nodes)
        for prop in common_props:
            self._build_widget_for_property(prop, selected_nodes)

    def _get_common_properties(self, nodes):
        """
        Returns a list of properties that are identical (by name and type)
        across all selected nodes.
        """
        if not nodes: return []
        
        # Get properties of the first node
        reference_props = nodes[0].get_properties()
        
        final_props = []
        
        for ref_prop in reference_props:
            is_common = True
            for node in nodes[1:]:
                # Check if this node has a matching property
                # We match by attr_name and class type
                node_props = node.get_properties()
                match = next((p for p in node_props 
                              if p.attr_name == ref_prop.attr_name 
                              and isinstance(p, type(ref_prop))), None)
                if not match:
                    is_common = False
                    break
            
            if is_common:
                final_props.append(ref_prop)
                
        return final_props

    def _clear_layout(self):
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _build_widget_for_property(self, prop, nodes):
        widget = None

        # --- STRING WIDGET ---
        if isinstance(prop, StringProperty):
            widget = QtWidgets.QLineEdit()
            if prop.placeholder: widget.setPlaceholderText(prop.placeholder)

            # USE NEW GETTER:
            values = [prop.get_value(n) for n in nodes]
            
            if len(set(values)) == 1:
                widget.setText(str(values[0]))
            else:
                widget.setPlaceholderText("--- Mixed ---")
                widget.clear()

            # USE NEW SETTER:
            widget.editingFinished.connect(
                lambda: self._apply_value(prop, nodes, widget.text())
            )

        # --- INT WIDGET ---
        elif isinstance(prop, IntProperty):
            widget = QtWidgets.QSpinBox()
            widget.setRange(prop.min_val, prop.max_val)

            # 1. Get Values
            values = [int(prop.get_value(n)) for n in nodes]
            unique_values = set(values)
            
            # The value we want to start at if the user touches the control
            sensible_default = values[0] if values else 0

            # 2. Setup "Mixed" State
            is_mixed = False
            if len(unique_values) == 1:
                widget.setValue(sensible_default)
            else:
                is_mixed = True
                # Park at minimum so the text shows up
                widget.setValue(prop.min_val) 
                widget.setSpecialValueText("--- Mixed ---")

            # 3. Define the Signal Logic
            # We use a mutable container (dict) for 'is_mixed' so the inner 
            # function can modify the flag from the outer scope.
            state = {'mixed': is_mixed}

            def on_int_changed(new_val):
                if state['mixed']:
                    # --- INTERCEPT THE FIRST INTERACTION ---
                    
                    widget.blockSignals(True)
                    
                    # Snap to the sensible default immediately
                    widget.setValue(sensible_default)
                    
                    # Clear the "Mixed" text so it looks like a normal number now
                    widget.setSpecialValueText("")
                    
                    widget.blockSignals(False)
                    
                    # Turn off the flag so next time it behaves normally
                    state['mixed'] = False
                    
                    # Option A: Apply the 'sensible_default' to the nodes immediately
                    self._apply_value(prop, nodes, sensible_default)
                    
                    # Option B: Do nothing else. 
                    # The user clicks "Up", the box snaps to "50" (default). 
                    # They have to click "Up" again to go to "51". 
                    # This is often safer to prevent accidental jumps.
                    
                else:
                    # --- NORMAL BEHAVIOR ---
                    self._apply_value(prop, nodes, new_val)

            widget.valueChanged.connect(on_int_changed)

        # --- BOOL ---
        elif isinstance(prop, BoolProperty):
            widget = QtWidgets.QCheckBox()
            
            # 1. GET VALUES
            values = [bool(prop.get_value(n)) for n in nodes]
            unique_values = set(values)

            # 2. SET INITIAL STATE
            if len(unique_values) == 1:
                state = list(unique_values)[0]
                widget.setCheckState(QtCore.Qt.Checked if state else QtCore.Qt.Unchecked)
                widget.setTristate(False) 
            else:
                widget.setTristate(True)
                widget.setCheckState(QtCore.Qt.PartiallyChecked)

            # 3. DEFINE SIGNAL LOGIC
            # We accept the argument 'state', but we cast it to int to be safe.
            def on_bool_changed(state):
                state_int = int(state) # Force to python integer (0, 1, or 2)
                
                # 0 = Unchecked
                # 1 = PartiallyChecked (Mixed)
                # 2 = Checked

                # If the state is 'Mixed' (1), it usually means the user is cycling 
                # through the tristate. We generally don't want to save "Mixed" to the node.
                if state_int == 1:
                    return

                # Determine True/False based on the integer, not the Enum
                new_bool_value = (state_int == 2)
                
                # Apply value
                self._apply_value(prop, nodes, new_bool_value)

                # Visual Polish: Once edited, it's no longer mixed.
                widget.setTristate(False)

            # 4. CONNECT SIGNAL
            widget.stateChanged.connect(on_bool_changed)

        if widget:
            self.form_layout.addRow(prop.label, widget)
            self._active_widgets.append(widget)

            # --- CHECK FOR PRIMARY FLAG ---
            if prop.is_primary:
                self._primary_widget = widget

    def _apply_value(self, prop, nodes, value):
        """Applies value using the property's internal logic."""
        for node in nodes:
            # The property object itself handles the complexity now
            prop.set_value(node, value)
        
        print(f"Updated {prop.label} for {len(nodes)} nodes.")

    def _on_quick_edit_shortcut(self):
        """Restores the behavior: Focus if unfocused, Clear if focused."""
        if not self._primary_widget:
            return

        # Check if the primary widget currently has focus
        if not self._primary_widget.hasFocus():
            # Bring panel to front (if floating/docked)
            self.raise_() 
            self.activateWindow()
            
            # Focus and Select All text
            self._primary_widget.setFocus()
            
            # If it's a LineEdit or SpinBox, select the text for easy overwriting
            if hasattr(self._primary_widget, "selectAll"):
                self._primary_widget.selectAll()
        else:
            # If already focused, clear focus (User hit Enter to "submit")
            self._primary_widget.clearFocus()
            # Optional: Return focus to the Graph/Canvas
            # self.graph.setFocus()