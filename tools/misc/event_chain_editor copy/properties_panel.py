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
        super().__init__(label, attr_name, **kwargs)

class TextProperty(NodeProperty):
    """Used for multi-line text descriptions/notes."""
    def __init__(self, label, attr_name, placeholder="", **kwargs):
        super().__init__(label, attr_name, **kwargs)
        self.placeholder = placeholder

class ButtonProperty(NodeProperty):
    def __init__(self, label, callback, button_text="Execute", **kwargs):
        super().__init__(label, attr_name=None, **kwargs)
        self.callback = callback
        self.button_text = button_text


class CommitPlainTextEdit(QtWidgets.QPlainTextEdit):
    """
    A QPlainTextEdit that emits 'editingFinished' when it loses focus
    or when the user presses Ctrl+Enter.
    """
    editingFinished = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabChangesFocus(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        self.setMaximumHeight(150) 
        self.setMinimumHeight(60) 

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.editingFinished.emit()

    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_Return and 
                event.modifiers() & QtCore.Qt.ControlModifier):
            self.clearFocus()
            return
        super().keyPressEvent(event)


class PropertiesPanel(QtWidgets.QDockWidget):
    def __init__(self, main_window, graph):
        super().__init__("Properties Panel", main_window)
        self.graph = graph
        
        # Main Container
        self.container = QtWidgets.QWidget()
        self.form_layout = QtWidgets.QFormLayout(self.container)
        self.form_layout.setContentsMargins(10, 10, 10, 10)
        self.setWidget(self.container)

        # Store active widget references
        self._active_widgets = [] 

        # Connect Graph Signals
        self.graph.node_selection_changed.connect(self.refresh_panel)

        self._primary_widget = None
        self.shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), main_window)
        self.shortcut.activated.connect(self._on_quick_edit_shortcut)

    def refresh_panel(self):
        """
        Triggered by the signal. We use a singleShot timer to defer the 
        UI build by one event loop tick. This ensures the Graph has fully 
        updated its internal selection list before we query it.
        """
        QtCore.QTimer.singleShot(0, self._build_ui)

    def _build_ui(self):
        """The actual logic to clear and rebuild the panel."""
        self._clear_layout()
        self._active_widgets = []
        self._primary_widget = None 

        # Now this will return the CORRECT list because the event loop cleared
        selected_nodes = self.graph.selected_nodes()
        if not selected_nodes: return

        common_props = self._get_common_properties(selected_nodes)
        for prop in common_props:
            self._build_widget_for_property(prop, selected_nodes)

    def _get_common_properties(self, nodes):
        if not nodes: return []
        
        reference_props = nodes[0].get_properties()
        final_props = []
        
        for ref_prop in reference_props:
            is_common = True
            for node in nodes[1:]:
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

            values = [prop.get_value(n) for n in nodes]
            
            if len(set(values)) == 1:
                widget.setText(str(values[0]))
            else:
                widget.setPlaceholderText("--- Mixed ---")
                widget.clear()

            widget.editingFinished.connect(
                lambda: self._apply_value(prop, nodes, widget.text())
            )

        # --- TEXT (MULTI-LINE) WIDGET ---
        elif isinstance(prop, TextProperty):
            widget = CommitPlainTextEdit()
            if prop.placeholder: 
                widget.setPlaceholderText(prop.placeholder)

            values = [str(prop.get_value(n)) for n in nodes]
            
            if len(set(values)) == 1:
                widget.setPlainText(values[0])
            else:
                widget.setPlaceholderText("--- Mixed ---")
                widget.setPlainText("")

            # Handle Newlines
            val = values[0].replace('\\n', '\n') 
            widget.setPlainText(val)

            widget.editingFinished.connect(
                lambda: self._apply_value(prop, nodes, widget.toPlainText().replace('\n', '\\n'))
            )

        # --- BUTTON WIDGET ---
        elif isinstance(prop, ButtonProperty):
            widget = QtWidgets.QPushButton(prop.button_text)
            
            def on_button_clicked():
                for node in nodes:
                    prop.callback(node)
                self.refresh_panel()
            
            widget.clicked.connect(on_button_clicked)

        # --- INT WIDGET ---
        elif isinstance(prop, IntProperty):
            widget = QtWidgets.QSpinBox()
            widget.setRange(prop.min_val, prop.max_val)

            values = [int(prop.get_value(n)) for n in nodes]
            unique_values = set(values)
            
            sensible_default = values[0] if values else 0

            is_mixed = False
            if len(unique_values) == 1:
                widget.setValue(sensible_default)
            else:
                is_mixed = True
                widget.setValue(prop.min_val) 
                widget.setSpecialValueText("--- Mixed ---")

            state = {'mixed': is_mixed}

            def on_int_changed(new_val):
                if state['mixed']:
                    widget.blockSignals(True)
                    widget.setValue(sensible_default)
                    widget.setSpecialValueText("")
                    widget.blockSignals(False)
                    state['mixed'] = False
                    self._apply_value(prop, nodes, sensible_default)
                else:
                    self._apply_value(prop, nodes, new_val)

            widget.valueChanged.connect(on_int_changed)

        # --- BOOL ---
        elif isinstance(prop, BoolProperty):
            widget = QtWidgets.QCheckBox()
            
            values = [bool(prop.get_value(n)) for n in nodes]
            unique_values = set(values)

            if len(unique_values) == 1:
                state = list(unique_values)[0]
                widget.setCheckState(QtCore.Qt.Checked if state else QtCore.Qt.Unchecked)
                widget.setTristate(False) 
            else:
                widget.setTristate(True)
                widget.setCheckState(QtCore.Qt.PartiallyChecked)

            def on_bool_changed(state):
                state_int = int(state)
                if state_int == 1: return
                new_bool_value = (state_int == 2)
                self._apply_value(prop, nodes, new_bool_value)
                widget.setTristate(False)

            widget.stateChanged.connect(on_bool_changed)

        if widget:
            self.form_layout.addRow(prop.label, widget)
            self._active_widgets.append(widget)

            if prop.is_primary:
                self._primary_widget = widget

    def _apply_value(self, prop, nodes, value):
        for node in nodes:
            prop.set_value(node, value)
        print(f"Updated {prop.label} for {len(nodes)} nodes.")

    def _on_quick_edit_shortcut(self):
        if not self._primary_widget:
            return

        if not self._primary_widget.hasFocus():
            self.raise_() 
            self.activateWindow()
            self._primary_widget.setFocus()
            if hasattr(self._primary_widget, "selectAll"):
                self._primary_widget.selectAll()
        else:
            self._primary_widget.clearFocus()