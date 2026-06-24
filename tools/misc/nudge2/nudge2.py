import sys
import os
import numpy as np
import random # Imported for the dummy color generator
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QMainWindow, QToolBar, 
                               QLabel, QWidget, QComboBox, QCheckBox, 
                               QPushButton, QDialog, QFormLayout, QDialogButtonBox,
                               QVBoxLayout, QSpinBox, QLineEdit, QHBoxLayout, QTextEdit, QTabWidget, QFileDialog,
                               QTableWidget, QTableWidgetItem, QAbstractItemView)
from PySide6.QtGui import (QPixmap, QPainter, QImage, QColor, QMouseEvent, 
                           QAction, QActionGroup, QCursor, QKeySequence, QShortcut)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QSize

# --- IMPORT PILLOW (Robust DDS Support) ---
try:
    from PIL import Image
except ImportError:
    print("CRITICAL: Pillow not found. Run 'pip install Pillow' to fix DDS loading.")

# Assuming this exists based on your upload
from definitioncsv import *
from relax_provinces import *


# --- CONFIGURATION ---
BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve() 
HARDCODED_IMAGE_PATH = BASE_PATH / "map" / "provinces.bmp"
OVERLAY_PATH = BASE_PATH / "map" / "terrain" / "colormap_rgb_cityemissivemask_a.dds"
#OVERLAY_PATH = BASE_PATH / "map" / "rivers.bmp" # works with several other files too (terrain, height etc.)

# Your Custom Map Modes
MAP_MODES = [
    ("Province", 8),
    ("Terrain", 9),
    ("Type", 10),
    ("Coastal", 11),
    ("Continent", 12),
    ("State", 14),
    ("Strat Region", 16),
    ("Impassable", 18),
    ("VP/Buildings", 19),
    ("Countries", 21),
]

# ============================================================
#  GLOBAL LUT CONFIGURATION
# ============================================================

base_lut = np.indices((256, 256, 256), dtype=np.uint8).transpose(1, 2, 3, 0)
lut = base_lut.copy()
selected_colors = set() 

def selected_colors_to_provinces():
    ret = []
    csv = get_definition_csv()
    for row in csv:
        col = (row[1], row[2], row[3])
        if col in selected_colors:
            ret.append(row[0])
    return ret

def update_composite_lut():
    global lut, base_lut, selected_colors
    lut = base_lut.copy()
    if selected_colors:
        for (r, g, b) in selected_colors:
            if 0 <= r < 256 and 0 <= g < 256 and 0 <= b < 256:
                lut[r, g, b] = [0, 0, 255]

def generate_lut(target_column_index, use_mixed_mode=False):
    """
    Generates the BASE lookup table from CSV.
    """
    print(f"Generating Base LUT (Col: {target_column_index}, Mixed: {use_mixed_mode})...")
    
    global base_lut
    
    # --- FIX START ---
    # 1. Generate indices: Shape (256, 256, 256, 3) where value is [R, G, B]
    indices = np.indices((256, 256, 256), dtype=np.uint8).transpose(1, 2, 3, 0)
    
    # 2. Reverse the last dimension to make the default mapping [B, G, R]
    # This ensures that undefined/new colors are displayed correctly in QImage (which uses BGR)
    base_lut = indices[..., ::-1].copy()
    # --- FIX END ---

    try:
        csv = get_expanded_definition()
        for row in csv:
            if target_column_index < len(row):
                target_val = row[target_column_index]
                
                if hasattr(target_val, '__getitem__') and len(target_val) >= 3:
                    # CSV is likely RGB, we need BGR for QImage
                    target_bgr = np.array(target_val[::-1], dtype=np.float32)
                    final_color = target_bgr

                    if use_mixed_mode:
                        base_bgr = np.array([row[3], row[2], row[1]], dtype=np.float32)
                        mixed = (target_bgr * 0.8) + (base_bgr * 0.2)
                        final_color = mixed

                    # row[1]=R, row[2]=G, row[3]=B
                    base_lut[row[1], row[2], row[3]] = final_color.astype(np.uint8)
    except Exception as e:
        print(f"Error generating LUT: {e}")
    
    # After generating base, rebuild the active LUT (to keep selection if any)
    update_composite_lut()
    return lut

lut = generate_lut(MAP_MODES[0][1], False)

class ClickableLabel(QLabel):
    clicked = Signal() # Signal to fire when clicked

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


# ============================================================
#  MODE SYSTEM
# ============================================================

class ToolMode:
    def getName(self): return "Base"
    def on_left_click(self, view, x, y, color): pass
    def on_left_drag(self, view, x, y, color): pass
    def on_right_click(self, view, x, y, color): pass
    def on_right_drag(self, view, x, y, color): pass
    def on_shift_click(self, view, x, y, color): pass
    def on_alt_click(self, view, x, y, color): pass

class PaintMode(ToolMode):
    def getName(self): return "Drawing"

    def on_left_click(self, view, x, y, color):
        view.perform_paint(x, y)

    def on_left_drag(self, view, x, y, color):
        view.perform_paint(x, y)

    def on_alt_click(self, view, x, y, color):
        view.set_active_color(color)

class SelectionMode(ToolMode):
    def __init__(self):
        super().__init__()
        # Initialize coordinates to track the previous click
        self.last_x = 0
        self.last_y = 0

    def getName(self): return "Selection"

    def _update_selection(self, view, x, y, color, keep_existing=False):
        global selected_colors
        rgb_key = (color.red(), color.green(), color.blue())
        
        # 1. Update the Selection Data
        already_in = rgb_key in selected_colors
        if not keep_existing:
            selected_colors.clear()
            if not already_in:
                selected_colors.add(rgb_key)
        else:
            if not already_in:
                selected_colors.add(rgb_key)
            else:
                selected_colors.remove(rgb_key)
        
        # 2. Update the Global LUT
        update_composite_lut()
        
        radius = 300
        
        # 3. Handle Visual Updates
        # Define the area around the NEW click
        new_rect = QRectF(x - radius, y - radius, radius * 2, radius * 2)
        
        if not keep_existing:
            # If we are NOT keeping the existing selection, we must 
            # forcefully redraw the OLD location to "turn off" its highlight.
            old_rect = QRectF(self.last_x - radius, self.last_y - radius, radius * 2, radius * 2)
            
            # Optimization: If the old and new rects overlap or are close, 
            # we could unite them, but calling refresh twice is usually 
            # faster than redrawing the huge empty space between two distant points.
            view.refresh_viewport(old_rect)

        # Always redraw the new location
        view.refresh_viewport(new_rect)

        # 4. Save position for next time
        self.last_x = x
        self.last_y = y

    def on_left_click(self, view, x, y, color):
        self._update_selection(view, x, y, color, keep_existing=False)

    def on_left_drag(self, view, x, y, color):
        self._update_selection(view, x, y, color, keep_existing=True)

    def on_shift_click(self, view, x, y, color):
        self._update_selection(view, x, y, color, keep_existing=True)

    def on_right_click(self, view, x, y, color):
        global selected_colors
        selected_colors.clear()
        update_composite_lut()
        # Full refresh is acceptable on clear, or we could use last_x/y here too
        view.refresh_viewport()

class ViewMode(ToolMode):
    def getName(self): return "View"
    # Inherits empty click/drag methods from ToolMode, 
    # so clicking does nothing (safe viewing).

# ============================================================
#  DIALOGUE FORMS (Unchanged)
# ============================================================
class CreateStateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create State")
        self.setModal(True)
        self.setMinimumWidth(300)
        layout = QVBoxLayout()
        self.setLayout(layout)
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Minas Tirith")
        form_layout.addRow("State Name:", self.name_input)
        self.owner_input = QLineEdit()
        self.owner_input.setPlaceholderText("MOR")
        form_layout.addRow("State Owner:", self.owner_input)
        layout.addLayout(form_layout)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept) 
        self.buttons.rejected.connect(self.reject) 
        layout.addWidget(self.buttons)

    def get_data(self):
        return {"state_name": self.name_input.text(), "state_owner": self.owner_input.text()}
    
class CreateRegionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Strategic Region")
        self.setModal(True)
        self.setMinimumWidth(300)
        layout = QVBoxLayout()
        self.setLayout(layout)
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Minas Tirith")
        form_layout.addRow("Region Name:", self.name_input)
        layout.addLayout(form_layout)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept) 
        self.buttons.rejected.connect(self.reject) 
        layout.addWidget(self.buttons)

    def get_data(self):
        return {"region_name": self.name_input.text()}
    
class TransferProvsDialog(QDialog):
    def __init__(self, parent=None, ToStratRegion=False):
        super().__init__(parent)
        self.setWindowTitle("Transfer Provinces")
        self.setModal(True)
        self.setMinimumWidth(300)
        layout = QVBoxLayout()
        self.setLayout(layout)
        if not ToStratRegion:
            states = get_all_states()
        else:
            states = get_all_stratregion()
        provs = selected_colors_to_provinces()
        state_loc = LocFile(STATES_LOC_DIR)
        av_states = []
        for p in provs:
            for st in states:
                if p in st.province_list:
                    if st not in av_states: av_states.append(st)
        form_layout = QFormLayout()
        self.available_states = QComboBox()
        for av_st in av_states:

            if ToStratRegion:
                st_id = av_st.region_id
                av_st_id = str(av_st.region_id)
            else:
                st_id = av_st.state_id
                av_st_id = str(av_st.state_id)

            av_st_name = state_loc.get(str(av_st.pObj.GetVal("name")).replace('"', ''))
            if av_st_name is None: av_st_name = ""
            self.available_states.addItem(av_st_id + "  " + av_st_name, st_id)
        form_layout.addRow("Target:", self.available_states)
        layout.addLayout(form_layout)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept) 
        self.buttons.rejected.connect(self.reject) 
        layout.addWidget(self.buttons)

    def get_data(self):
        return {"target_state": self.available_states.currentData()}

class ProvincePropertiesDialog(QDialog):
    # Shared configuration
    PROPERTIES_CONFIG = {
        "type":      ["land", "sea", "lake"],
        "coastal":   ["true", "false"],
        "terrain":   [
            "unknown", "ocean", "lakes", "forest", "hills", "mountain", 
            "plains", "dark_grounds", "urban", "jungle", "marsh", 
            "desert", "water_fjords", "water_shallow_sea", "water_deep_ocean",
            "tunnels", "moria", "khazaddum", "abyss"
        ],
        "continent": [str(i) for i in range(16)] # 0-15
    }

    def __init__(self, current_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Province Properties")
        self.setModal(True)
        self.resize(400, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- 1. INFO SECTION (Read Only) ---
        lbl_info = QLabel("Selection Info:")
        lbl_info.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(lbl_info)

        self.info_area = QTextEdit()
        self.info_area.setPlainText(current_data.get("info", ""))
        self.info_area.setReadOnly(True)
        self.info_area.setMaximumHeight(100)
        self.info_area.setStyleSheet("background-color: #f0f0f0; color: #333;")
        self.layout.addWidget(self.info_area)

        self.layout.addSpacing(10)
        self.layout.addWidget(QLabel("Edit Properties (Check to Overwrite):"))
        
        self.widgets = {}

        form_layout = QFormLayout()

        for key, options in self.PROPERTIES_CONFIG.items():
            # Current value from selection
            cur_val = current_data.get(key, "unknown")
            is_mixed = cur_val == "-- mixed --"

            # The Checkbox (Enable editing)
            # Label includes the key name
            chk = QCheckBox(key.capitalize())
            chk.setChecked(False) # Default to OFF so we don't accidentally overwrite mixed values
            
            # The Combobox
            combo = QComboBox()
            
            # Populate Combo
            # If mixed, we add a specific item for it
            display_options = list(options)
            if is_mixed:
                display_options.insert(0, "-- mixed --")
            
            combo.addItems(display_options)
            
            # Select the current value
            index = combo.findText(cur_val, Qt.MatchFixedString)
            if index >= 0:
                combo.setCurrentIndex(index)
            
            combo.setEnabled(False) # Disabled until checkbox checked

            # Logic: Toggle enable
            chk.toggled.connect(combo.setEnabled)

            # Logic: Auto-check if user changes combo manually (Optional UX polish)
            # combo.activated.connect(lambda: chk.setChecked(True)) 

            # Layout: Checkbox on left, Combo on right
            form_layout.addRow(chk, combo)
            
            self.widgets[key] = (chk, combo)

        self.layout.addLayout(form_layout)

        # --- 3. BUTTONS ---
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        """
        Returns only the properties where the checkbox is CHECKED.
        """
        result = {}
        for key, (chk, combo) in self.widgets.items():
            if chk.isChecked():
                val = combo.currentText()
                # Don't submit "-- mixed --" if the user checked the box but didn't pick a real value
                if val != "-- mixed --":
                    result[key] = val
        return result
    
class StatePropertiesDialog(QDialog):
    # predefined categories for the dropdown
    CATEGORIES = [
        "wasteland", "enclave", "tiny_island", "pastoral", "rural", 
        "town", "large_town", "city", "large_city", "metropolis", "megalopolis"
    ]

    def __init__(self, current_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("State Properties")
        self.setModal(True)
        self.resize(400, 450)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- 1. INFO SECTION (Read Only) ---
        lbl_info = QLabel("State Info:")
        lbl_info.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(lbl_info)

        self.info_area = QTextEdit()
        self.info_area.setPlainText(current_data.get("info", ""))
        self.info_area.setReadOnly(True)
        self.info_area.setMaximumHeight(80)
        self.info_area.setStyleSheet("background-color: #f0f0f0; color: #333;")
        self.layout.addWidget(self.info_area)

        self.layout.addSpacing(10)
        self.layout.addWidget(QLabel("Edit Properties (Check to Overwrite):"))

        self.widgets = {}
        form_layout = QFormLayout()

        # Helper to add rows dynamically based on widget type
        def add_row(key, label_text, widget_obj, val_list=None):
            cur_val = current_data.get(key, "")
            is_mixed = cur_val == "-- mixed --"

            # The Checkbox
            chk = QCheckBox(label_text)
            chk.setChecked(False)

            # Configure Widget
            if isinstance(widget_obj, QComboBox) and val_list:
                display_options = list(val_list)
                if is_mixed:
                    display_options.insert(0, "-- mixed --")
                widget_obj.addItems(display_options)
                
                # Set Index
                index = widget_obj.findText(cur_val, Qt.MatchFixedString)
                if index >= 0:
                    widget_obj.setCurrentIndex(index)
            
            elif isinstance(widget_obj, QLineEdit):
                widget_obj.setText(cur_val)
                if is_mixed:
                    widget_obj.setPlaceholderText("-- mixed --")
                    widget_obj.setText("") # Clear text so they don't accidentally save "-- mixed --"

            widget_obj.setEnabled(False)
            chk.toggled.connect(widget_obj.setEnabled)

            form_layout.addRow(chk, widget_obj)
            self.widgets[key] = (chk, widget_obj)

        # --- 2. INPUT FIELDS ---
        
        # Name (Text Field)
        add_row("name", "State Name", QLineEdit())

        # Impassable (Yes/No)
        add_row("impassable", "Impassable", QComboBox(), ["yes", "no"])

        # Category (Dropdown)
        add_row("state_category", "Category", QComboBox(), self.CATEGORIES)

        self.layout.addLayout(form_layout)

        # --- 3. BUTTONS ---
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        """ Returns only the properties where the checkbox is CHECKED. """
        result = {}
        for key, (chk, widget) in self.widgets.items():
            if chk.isChecked():
                val = None
                if isinstance(widget, QComboBox):
                    val = widget.currentText()
                elif isinstance(widget, QLineEdit):
                    val = widget.text()
                
                # Validation: Don't submit mixed placeholders
                if val != "-- mixed --":
                    result[key] = val
        return result


class VictoryPointsDialog(QDialog):
    """Dialog to view and edit Victory Points for selected provinces."""

    def __init__(self, vps, provinces, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Victory Points")
        self.setModal(True)
        self.resize(500, 400)

        self._selected_provinces = list(provinces) if provinces is not None else []

        layout = QVBoxLayout()
        self.setLayout(layout)

        info_label = QLabel("Victory Points for selected provinces:")
        layout.addWidget(info_label)

        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Province ID", "Value", "Name"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        layout.addWidget(self.table)

        # Populate existing VPs
        for vp in vps:
            self._add_row(vp.get("province", 0), vp.get("value", 0), vp.get("name", ""))

        # Controls for adding/removing rows
        controls_layout = QHBoxLayout()

        btn_add = QPushButton("Add VP")
        #btn_remove = QPushButton("Remove Selected")

        btn_add.clicked.connect(self._on_add_row)
        #btn_remove.clicked.connect(self._on_remove_selected)

        controls_layout.addWidget(btn_add)
        #controls_layout.addWidget(btn_remove)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _add_row(self, province_id=0, value=0, name=""):
        row = self.table.rowCount()
        self.table.insertRow(row)

        spin_prov = QSpinBox()
        spin_prov.setRange(0, 999999)
        spin_prov.setValue(int(province_id))

        spin_value = QSpinBox()
        spin_value.setRange(0, 1000)
        spin_value.setValue(int(value))

        line_name = QLineEdit()
        line_name.setText(name if name is not None else "")

        self.table.setCellWidget(row, 0, spin_prov)
        self.table.setCellWidget(row, 1, spin_value)
        self.table.setCellWidget(row, 2, line_name)

        # Provide a visual row label (optional, but nice UX)
        self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(row + 1)))

    def _on_add_row(self):
        # Default province: first selected province if available
        default_prov = self._selected_provinces[0] if self._selected_provinces else 0
        self._add_row(default_prov, 1, "")

    def _on_remove_selected(self):
        selected_rows = {idx.row() for idx in self.table.selectedIndexes()}
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)

    def get_vps(self):
        """Return list of VP dicts suitable for set_victory_points."""
        result = []
        for row in range(self.table.rowCount()):
            spin_prov = self.table.cellWidget(row, 0)
            spin_value = self.table.cellWidget(row, 1)
            line_name = self.table.cellWidget(row, 2)

            if not spin_prov or not spin_value or not line_name:
                continue

            prov_id = int(spin_prov.value())
            value = int(spin_value.value())
            name = line_name.text().strip()

            result.append({
                "province": prov_id,
                "value": value,
                "name": name,
            })

        return result

class FindProvinceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find Province")
        self.setModal(True)
        self.setFixedSize(300, 200) # Slightly taller for tabs

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- TAB 1: Search by ID (Default) ---
        self.tab_id = QWidget()
        id_layout = QFormLayout()
        self.tab_id.setLayout(id_layout)
        
        self.spin_id = QSpinBox()
        self.spin_id.setRange(0, 999999) # High range for Map IDs
        self.spin_id.setButtonSymbols(QSpinBox.NoButtons)
        #self.spin_id.setPlaceholderText("e.g. 4521")
        
        id_layout.addRow("Province ID:", self.spin_id)
        self.tabs.addTab(self.tab_id, "By ID")

        # --- TAB 2: Search by Color ---
        self.tab_color = QWidget()
        color_layout = QFormLayout()
        self.tab_color.setLayout(color_layout)

        self.spin_r = QSpinBox()
        self.spin_g = QSpinBox()
        self.spin_b = QSpinBox()

        for spin in [self.spin_r, self.spin_g, self.spin_b]:
            spin.setRange(0, 255)
            spin.setButtonSymbols(QSpinBox.NoButtons)

        color_layout.addRow("Red:", self.spin_r)
        color_layout.addRow("Green:", self.spin_g)
        color_layout.addRow("Blue:", self.spin_b)
        
        self.tabs.addTab(self.tab_color, "By Color")

        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_result(self):
        """
        Returns a tuple: (found_success, (r, g, b))
        """
        # Check which tab is currently active
        if self.tabs.currentIndex() == 0:
            # --- ID MODE ---
            prov_id = self.spin_id.value()
            try:
                # Call the external function from definitioncsv
                color = get_prov_color_from_id(prov_id)
                
                # Validation: Ensure we actually got a color back
                if color and len(color) == 3:
                    # definitioncsv usually returns list/tuple, e.g. [120, 50, 60]
                    return True, (int(color[0]), int(color[1]), int(color[2]))
                else:
                    print(f"ID {prov_id} exists but has no valid color definition.")
                    return False, None
            except Exception as e:
                print(f"Error looking up ID {prov_id}: {e}")
                return False, None

        else:
            # --- COLOR MODE ---
            return True, (self.spin_r.value(), self.spin_g.value(), self.spin_b.value())
        

class GoToCoordDialog(QDialog):
    def __init__(self, max_w, max_h, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Go To Coordinates")
        self.setModal(True)
        self.setFixedSize(250, 150)

        layout = QVBoxLayout()
        self.setLayout(layout)
        form = QFormLayout()

        # X Coordinate
        self.spin_x = QSpinBox()
        self.spin_x.setRange(0, max_w)
        self.spin_x.setButtonSymbols(QSpinBox.NoButtons)
        self.spin_x.setValue(0)
        
        # Y Coordinate
        self.spin_y = QSpinBox()
        self.spin_y.setRange(0, max_h)
        self.spin_y.setButtonSymbols(QSpinBox.NoButtons)
        self.spin_y.setValue(0)

        form.addRow("X:", self.spin_x)
        form.addRow("Y:", self.spin_y)
        layout.addLayout(form)

        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        
        # Focus X immediately
        self.spin_x.setFocus()

    def get_coords(self):
        return self.spin_x.value(), self.spin_y.value()


class SetColorDialog(QDialog):
    def __init__(self, current_color=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Custom Color")
        self.setModal(True)
        self.setFixedSize(250, 180)

        layout = QVBoxLayout()
        self.setLayout(layout)
        form = QFormLayout()

        # Defaults
        r_def, g_def, b_def = 0, 0, 0
        if current_color and current_color.isValid():
            r_def, g_def, b_def = current_color.red(), current_color.green(), current_color.blue()

        # R
        self.spin_r = QSpinBox()
        self.spin_r.setRange(0, 255)
        self.spin_r.setButtonSymbols(QSpinBox.NoButtons)
        self.spin_r.setValue(r_def)
        
        # G
        self.spin_g = QSpinBox()
        self.spin_g.setRange(0, 255)
        self.spin_g.setButtonSymbols(QSpinBox.NoButtons)
        self.spin_g.setValue(g_def)

        # B
        self.spin_b = QSpinBox()
        self.spin_b.setRange(0, 255)
        self.spin_b.setButtonSymbols(QSpinBox.NoButtons)
        self.spin_b.setValue(b_def)

        form.addRow("Red:", self.spin_r)
        form.addRow("Green:", self.spin_g)
        form.addRow("Blue:", self.spin_b)
        layout.addLayout(form)

        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.spin_r.setFocus()

    def get_color(self):
        return QColor(self.spin_r.value(), self.spin_g.value(), self.spin_b.value())
    

class RelaxSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Relax Options")
        self.setModal(True)
        self.setFixedSize(300, 180)

        layout = QVBoxLayout()
        self.setLayout(layout)
        form = QFormLayout()

        # Iterations
        self.spin_iter = QSpinBox()
        self.spin_iter.setRange(1, 100)
        self.spin_iter.setValue(10) # Default
        self.spin_iter.setToolTip("How many times to apply the relaxation smoothing.")

        # Distortion Scale
        self.spin_scale = QSpinBox()
        self.spin_scale.setRange(1, 500)
        self.spin_scale.setValue(20) # Default
        self.spin_scale.setToolTip("Frequency of the noise. Lower = jagged, Higher = wavy.")

        # Distortion Magnitude
        self.spin_mag = QSpinBox()
        self.spin_mag.setRange(0, 100)
        self.spin_mag.setValue(3) # Default
        self.spin_mag.setToolTip("How far pixels can be pushed (strength).")

        form.addRow("Iterations:", self.spin_iter)
        form.addRow("Distortion Scale:", self.spin_scale)
        form.addRow("Distortion Mag:", self.spin_mag)
        layout.addLayout(form)

        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_values(self):
        return (self.spin_iter.value(), self.spin_scale.value(), self.spin_mag.value())


# ============================================================
#  VIEWER
# ============================================================

class EditorView(QGraphicsView):
    colorChanged = Signal(QColor)

    def __init__(self):
        super().__init__()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self.data_image = None 
        self.display_image = None
        self.image_item = None
        
        # Overlay Data
        self.overlay_alpha_map = None 
        self.use_overlay = False

        # --- FIX 1: Start with No Color ---
        self.current_color = None 
        
        # --- FIX 2: Start in View Mode ---
        # (Make sure ViewMode class is defined BEFORE EditorView in your file)
        self.current_mode = ViewMode() 
        self.brush_size = 10
        self.current_mode = PaintMode()

        # --- LOGIC FOR NEW PROVINCE CREATION ---
        self.pending_province_creation = False

        self._is_panning = False
        self._last_pan_pos = QPointF()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing, False)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        # REQUIRED: Allows us to track mouse movement without clicking button
        self.setMouseTracking(True) 
    
        # Make sure the view can catch key presses
        self.setFocusPolicy(Qt.StrongFocus)

    # Add this helper method to EditorView
    def _update_picker_cursor(self, mouse_pos):
        """
        Creates a dynamic cursor showing the color under the mouse.
        """
        x, y, color = self.get_interaction_data(mouse_pos)
        
        # 1. Create a transparent canvas for the cursor
        size = 32
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # 2. Draw the color bubble
        # White outline (visibility on dark colors)
        painter.setPen(QColor(255, 255, 255)) 
        painter.setBrush(color)
        painter.drawEllipse(2, 2, size - 5, size - 5)
        
        # Black inner outline (visibility on light colors)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QColor(0, 0, 0))
        painter.drawEllipse(3, 3, size - 7, size - 7)
        
        painter.end()
        
        # 3. Set the cursor
        self.setCursor(QCursor(pix))

    def _get_brush_cursor(self):
        """Generates a cursor that scales with the viewport zoom."""
        # 1. Get scale and Calculate sizes (Same as before)
        zoom_factor = self.transform().m11()
        visual_size = self.brush_size * zoom_factor
        display_d = max(visual_size, 4)
        canvas_size = int(display_d + 6)
        
        pix = QPixmap(canvas_size, canvas_size)
        pix.fill(Qt.transparent)
        
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        center = canvas_size / 2
        radius = display_d / 2
        
        # --- NEW: Visual Feedback for No Color ---
        if self.current_color is None:
            # Draw a Red "X" or "Prohibited" sign
            painter.setPen(QColor(255, 0, 0, 200)) # Red
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(center, center), radius, radius)
            # Draw Cross
            off = radius * 0.7
            painter.drawLine(QPointF(center - off, center - off), QPointF(center + off, center + off))
            painter.drawLine(QPointF(center + off, center - off), QPointF(center - off, center + off))
        
        # 3. Draw the cursor
        elif display_d <= 4:
            # Crosshair for very small visual sizes
            painter.setPen(QColor(0, 0, 0))
            painter.drawLine(int(center)-2, int(center), int(center)+2, int(center))
            painter.drawLine(int(center), int(center)-2, int(center), int(center)+2)
            painter.setPen(QColor(255, 255, 255))
            painter.drawPoint(int(center), int(center))
        else:
            # Circle
            painter.setPen(QColor(255, 255, 255)) # White outer
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(center, center), radius, radius)
            
            painter.setPen(QColor(0, 0, 0)) # Black inner
            painter.drawEllipse(QPointF(center, center), radius - 1, radius - 1)
            
        painter.end()
        
        return QCursor(pix, int(center), int(center))
    
    def find_pixel_by_color(self, r, g, b):
        """
        Scans the data image for the first occurrence of the specific RGB.
        Returns (x, y) tuple or None if not found.
        """
        if not self.data_image:
            return None

        # 1. Convert to NumPy (Use existing helper)
        # Shape is (Height, Width, 4)
        arr = self._qimage_to_numpy(self.data_image)

        # 2. Define target (QImage is BGR order at indices 0,1,2)
        # We need to find pixels where:
        # Blue channel (0) == b
        # Green channel (1) == g
        # Red channel (2) == r
        
        # Create a boolean mask
        # (This is very fast compared to Python loops)
        mask = (arr[:, :, 0] == b) & (arr[:, :, 1] == g) & (arr[:, :, 2] == r)

        # 3. Find indices
        # argwhere returns array of [row, col] -> [y, x]
        indices = np.argwhere(mask)

        if len(indices) > 0:
            # Return the first match (y, x) -> convert to (x, y)
            y, x = indices[0]
            return int(x), int(y)
        
        return None
    
    def update_active_cursor(self):
        """Decides which cursor to show based on Keys and Mode."""
        modifiers = QApplication.keyboardModifiers()
        
        # Priority 1: Alt Key (Color Picker)
        if modifiers & Qt.AltModifier:
            # We use the dynamic picker we made earlier
            # (Requires mouse position, will be updated by mouseMove)
            self._update_picker_cursor(self.mapFromGlobal(QCursor.pos()).toPointF())
            return

        # Priority 2: Paint Mode
        if isinstance(self.current_mode, PaintMode):
            self.setCursor(self._get_brush_cursor())
            return
            
        # Priority 3: Default
        self.setCursor(Qt.ArrowCursor)

    def set_brush_size(self, size):
        """Setter to ensure cursor updates immediately when size changes."""
        self.brush_size = size
        self.update_active_cursor()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Alt:
            # Immediately update cursor at current mouse position
            self._update_picker_cursor(self.mapFromGlobal(QCursor.pos()).toPointF())
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Alt:
            # When Alt is released, check what mode we are in and restore that cursor
            self.update_active_cursor()
        super().keyReleaseEvent(event)

    def emit_current_color(self):
        self.colorChanged.emit(self.current_color)
    
    def set_active_color(self, color):
        """Standard color pick (e.g. Alt+Click). Cancels pending creation."""
        self.current_color = color
        self.pending_province_creation = False # User manually picked a color, cancel specific logic
        self.colorChanged.emit(self.current_color)
        print(f"Color Picked: {color.name()} (Creation Trigger Cancelled)")

    def set_creation_color(self, color):
        """Sets a specific color and arms the 'New Province' trigger."""
        self.current_color = color # This enables painting (it is no longer None)
        self.pending_province_creation = True 
        self.colorChanged.emit(self.current_color)
        self.update_active_cursor() # Refresh cursor to remove the Red X
        print(f"Ready to create province with color: {color.name()}")

    def set_overlay_enabled(self, enabled):
        self.use_overlay = enabled
        self.refresh_viewport()

    def refresh_viewport(self, rect=None):
        if not self.data_image: return
        self.update_display(rect) 
        self.image_item.setPixmap(QPixmap.fromImage(self.display_image))

    def perform_paint(self, x, y):
        if not self.data_image: return

        if self.current_color is None:
            print("No color selected! Use Alt+Click to pick a color.")
            return

        # --- NEW PROVINCE LOGIC ---
        if self.pending_province_creation:
            if 0 <= x < self.data_image.width() and 0 <= y < self.data_image.height():
                old_qt_color = self.data_image.pixelColor(x, y)
                old_rgb = (old_qt_color.red(), old_qt_color.green(), old_qt_color.blue())
                new_rgb = (self.current_color.red(), self.current_color.green(), self.current_color.blue())
                create_new_province_from(old_rgb, new_rgb)
            self.pending_province_creation = False

        # 1. Modify Data
        painter = QPainter(self.data_image)
        painter.setBrush(self.current_color)
        painter.setPen(Qt.NoPen)
        painter.setRenderHint(QPainter.Antialiasing, False) 

        # --- BRUSH SHAPE LOGIC ---
        if self.brush_size == 1:
            painter.setPen(self.current_color)
            painter.drawPoint(x, y)
            
        elif self.brush_size == 2:
            # FIX: Force a 2x2 square. 
            # A radius-1 circle is unstable on integer grids.
            # (x-1, y-1) ensures the 2x2 block covers the pixel you clicked and the top-left neighbor.
            painter.drawRect(x - 1, y - 1, 2, 2)
            
        else:
            # For larger brushes, the centered ellipse works fine
            center_point = QPointF(x + 0.5, y + 0.5)
            radius = self.brush_size / 2.0
            painter.drawEllipse(center_point, radius, radius)

        painter.end()

        # 2. Update Display
        offset = self.brush_size / 2.0
        dirty_rect = QRectF(x - offset, y - offset, float(self.brush_size), float(self.brush_size))
        
        safe_rect = dirty_rect.adjusted(-2, -2, 2, 2)
        self.update_display(safe_rect)
        
        # 3. Refresh
        self.image_item.setPixmap(QPixmap.fromImage(self.display_image))

    # --- LUT / SHADER LOGIC (Unchanged) ---
    def _qimage_to_numpy(self, image):
        width = image.width()
        height = image.height()
        ptr = image.bits()
        arr = np.frombuffer(ptr, np.uint8).reshape((height, -1))
        return arr[:, :width * 4].reshape((height, width, 4))

    def update_display(self, rect=None):
        if not self.data_image or not self.display_image: return
        arr_data = self._qimage_to_numpy(self.data_image)
        arr_display = self._qimage_to_numpy(self.display_image)

        if rect:
            x1 = max(0, int(rect.left()))
            y1 = max(0, int(rect.top()))
            x2 = min(self.data_image.width(), int(rect.right()) + 1)
            y2 = min(self.data_image.height(), int(rect.bottom()) + 1)
        else:
            x1, y1 = 0, 0
            x2, y2 = self.data_image.width(), self.data_image.height()

        if x1 >= x2 or y1 >= y2: return

        b_indices = arr_data[y1:y2, x1:x2, 0]
        g_indices = arr_data[y1:y2, x1:x2, 1]
        r_indices = arr_data[y1:y2, x1:x2, 2]

        arr_display[y1:y2, x1:x2, 3] = arr_data[y1:y2, x1:x2, 3]
        arr_display[y1:y2, x1:x2, 0:3] = lut[r_indices, g_indices, b_indices]

        if self.use_overlay and self.overlay_alpha_map is not None:
            map_h, map_w = self.overlay_alpha_map.shape
            safe_x2 = min(x2, map_w)
            safe_y2 = min(y2, map_h)

            if safe_x2 > x1 and safe_y2 > y1:
                alpha_slice = self.overlay_alpha_map[y1:safe_y2, x1:safe_x2]
                alpha_factor = alpha_slice[:, :, np.newaxis]
                current_rgb = arr_display[y1:safe_y2, x1:safe_x2, 0:3].astype(np.float32)
                blended_rgb = current_rgb * alpha_factor
                arr_display[y1:safe_y2, x1:safe_x2, 0:3] = blended_rgb.astype(np.uint8)

    # --- IMAGE LOADING (Unchanged) ---
    def _load_overlay(self, width, height):
        if not os.path.exists(OVERLAY_PATH):
            return

        try:
            img = Image.open(OVERLAY_PATH)
            
            # Resize first to match dimensions
            if img.size != (width, height):
                img = img.resize((width, height), Image.Resampling.NEAREST)

            # --- LOGIC FIX START ---
            # Check if the image mode implies it has an alpha channel (RGBA, LA, etc.)
            # 'P' mode (Palette) requires checking 'transparency' info, usually rare for simple BMPs
            has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)

            if has_alpha:
                # IT IS A DDS/PNG (Native Transparency)
                img = img.convert("RGBA")
                arr = np.array(img)
                # Take the 4th channel (Alpha)
                raw_alpha = arr[:, :, 3].astype(np.float32) / 255.0
            else:
                # IT IS A BMP (No Transparency)
                # We assume the BMP is a black/white mask.
                # Convert to Grayscale ('L') effectively flattening RGB to one channel
                gray_img = img.convert("L") 
                arr = np.array(gray_img)
                # Use the pixel intensity (whiteness) as the alpha
                raw_alpha = arr.astype(np.float32) / 255.0
            # --- LOGIC FIX END ---

            brightness_factor = 2.0
            self.overlay_alpha_map = np.clip(raw_alpha * brightness_factor, 0.0, 1.0)
            
            print(f"Overlay loaded ({img.format} processed as {'Alpha-Channel' if has_alpha else 'Luminance-Mask'}).")

        except Exception as e:
            print(f"FAILED to load overlay via Pillow: {e}")

    def load_image(self, path):
        if not os.path.exists(path):
            print(f"Error: {path}")
            return
        img = QImage(path)
        if img.isNull(): return
        self.data_image = img.convertToFormat(QImage.Format_ARGB32)
        self.display_image = QImage(self.data_image.size(), QImage.Format_ARGB32)
        self._load_overlay(self.data_image.width(), self.data_image.height())
        self.update_display() 
        pixmap = QPixmap.fromImage(self.display_image)
        self._scene.clear()
        self.image_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self.image_item)
        self.setSceneRect(self.image_item.boundingRect())

    # --- INPUT ROUTING (Unchanged) ---
    def get_interaction_data(self, window_pos):
        if not self.image_item: return None, None, None
        scene_pos = self.mapToScene(window_pos.toPoint())
        item_pos = self.image_item.mapFromScene(scene_pos)
        x, y = int(item_pos.x()), int(item_pos.y())
        if 0 <= x < self.data_image.width() and 0 <= y < self.data_image.height():
            col = self.data_image.pixelColor(x, y)
            return x, y, col
        return x, y, QColor(0,0,0)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._last_pan_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        x, y, col = self.get_interaction_data(event.position())
        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ShiftModifier:
                self.current_mode.on_shift_click(self, x, y, col)
            elif event.modifiers() & Qt.AltModifier:
                self.current_mode.on_alt_click(self, x, y, col)
            else:
                self.current_mode.on_left_click(self, x, y, col)
        elif event.button() == Qt.RightButton:
            self.current_mode.on_right_click(self, x, y, col)
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            delta = event.position() - self._last_pan_pos
            self._last_pan_pos = event.position()
            hs = self.horizontalScrollBar()
            vs = self.verticalScrollBar()
            hs.setValue(hs.value() - delta.x())
            vs.setValue(vs.value() - delta.y())
            event.accept()
            return
        
        # If ALT is held but no buttons are clicked, update the color preview
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.AltModifier and not event.buttons():
            self._update_picker_cursor(event.position())
            # We don't call super() here because we don't want standard hover effects interfering
            return
    
        x, y, col = self.get_interaction_data(event.position())
        if event.buttons() & Qt.LeftButton:
            self.current_mode.on_left_drag(self, x, y, col)
        elif event.buttons() & Qt.RightButton:
            self.current_mode.on_right_drag(self, x, y, col)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event):
        zoom_in = 1.25
        zoom_out = 1 / zoom_in
        factor = zoom_in if event.angleDelta().y() > 0 else zoom_out
        self.scale(factor, factor)
        self.update_active_cursor()

# ============================================================
#  MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nudge Tool V2")
        self.resize(1200, 800) # Slightly wider to accommodate the dock

        self.paint_ui_actions = []
        self.select_ui_actions = []
        self.select_view_actions = []

        self.viewer = EditorView()
        self.setCentralWidget(self.viewer)
        self.viewer.colorChanged.connect(self.update_color_display)
        
        # --- CHANGED ORDER HERE ---
        self.setup_side_panel() # Create the panel first
        self.setup_toolbar()    # Create the toolbar second
        
        self.tab_shortcut = QShortcut(QKeySequence(Qt.Key_Tab), self)
        self.tab_shortcut.activated.connect(self.cycle_tool_mode)

        self.brush_shortcut = QShortcut(QKeySequence(Qt.Key_B), self)
        self.brush_shortcut.activated.connect(self.cycle_brush_size)

        self.viewer.load_image(HARDCODED_IMAGE_PATH)
        self.viewer.emit_current_color()

        # Set initial tool
        self.change_tool(0)

    def setup_toolbar(self):
        """Sets up the top toolbar strictly for Active Tool controls."""
        toolbar = QToolBar("Active Tool")
        toolbar.setIconSize(QSize(24, 24)) # Optional, requires QSize import
        self.addToolBar(toolbar)

        # 1. Main Tool Selector
        toolbar.addWidget(QLabel("  Active Tool:  "))
        self.tool_combo = QComboBox()
        self.tool_combo.addItem("View", ViewMode()) 
        self.tool_combo.addItem("Painting", PaintMode())
        self.tool_combo.addItem("Selection", SelectionMode()) 
        self.tool_combo.currentIndexChanged.connect(self.change_tool)
        toolbar.addWidget(self.tool_combo)
        
        toolbar.addSeparator()

        # ==========================================
        #  PAINTING TOOL UI (Dynamic)
        # ==========================================
        
        # New Province Generators
        btn_land = QPushButton("New Land")
        btn_land.clicked.connect(lambda checked=False: self.setup_new_province("land"))
        self.paint_ui_actions.append(toolbar.addWidget(btn_land))

        btn_lake = QPushButton("New Lake")
        btn_lake.clicked.connect(lambda checked=False: self.setup_new_province("lake"))
        self.paint_ui_actions.append(toolbar.addWidget(btn_lake))

        btn_sea = QPushButton("New Sea")
        btn_sea.clicked.connect(lambda checked=False: self.setup_new_province("sea"))
        self.paint_ui_actions.append(toolbar.addWidget(btn_sea))

        toolbar.addSeparator()

        # Brush Controls
        self.paint_ui_actions.append(toolbar.addWidget(QLabel(" Color: ")))
        
        self.color_display = ClickableLabel() 
        self.color_display.setFixedSize(24, 24)
        self.color_display.setCursor(Qt.PointingHandCursor) # Show hand cursor on hover
        self.color_display.setStyleSheet("border: 1px solid #999; background-color: transparent;")
        self.color_display.setToolTip("Click to set custom RGB")
        
        # 2. Connect the click signal
        self.color_display.clicked.connect(self.open_custom_color_dialog)
        
        self.paint_ui_actions.append(toolbar.addWidget(self.color_display))

        brush_group = QActionGroup(self)
        self.brush_sizes_list = [1, 2, 4, 6, 10] 
        self.brush_action_map = {} 

        for label, size in zip(["1px", "2px", "4px", "6px", "10px"], self.brush_sizes_list):
            action = QAction(label, self)
            action.setCheckable(True)
            if size == 10:
                action.setChecked(True)
                self.viewer.brush_size = size
            action.triggered.connect(lambda c, s=size: self.viewer.set_brush_size(s))
            brush_group.addAction(action)
            toolbar.addAction(action)
            self.paint_ui_actions.append(action)
            self.brush_action_map[size] = action

        # ==========================================
        #  SELECTION TOOL UI (Dynamic)
        # ==========================================

        self.btn_action1 = QPushButton("Create State")
        self.btn_action1.clicked.connect(self.create_state_func)
        self.select_ui_actions.append(toolbar.addWidget(self.btn_action1))

        self.btn_action2 = QPushButton("Transfer to State")
        self.btn_action2.clicked.connect(self.transfer_to_state_func)
        self.select_ui_actions.append(toolbar.addWidget(self.btn_action2))

        self.btn_action1_r = QPushButton("Create StratReg")
        self.btn_action1_r.clicked.connect(self.create_strategic_region_func)
        self.select_ui_actions.append(toolbar.addWidget(self.btn_action1_r))

        self.btn_action3 = QPushButton("Transfer to StratReg")
        self.btn_action3.clicked.connect(self.transfer_to_stratregion_func)
        self.select_ui_actions.append(toolbar.addWidget(self.btn_action3))

        self.btn_prov_props = QPushButton("Prov. Properties")
        self.btn_prov_props.clicked.connect(self.edit_province_properties_func)
        self.select_ui_actions.append(toolbar.addWidget(self.btn_prov_props))

        self.btn_state_props = QPushButton("State Properties")
        self.btn_state_props.clicked.connect(self.edit_state_properties_func)
        self.select_ui_actions.append(toolbar.addWidget(self.btn_state_props))

        self.btn_edit_vps = QPushButton("Edit VPs")
        self.btn_edit_vps.clicked.connect(self.edit_vps_func)
        self.select_ui_actions.append(toolbar.addWidget(self.btn_edit_vps))

        self.btn_split = QPushButton("Split Provinces")
        self.btn_split.clicked.connect(self.split_selected_provinces_func)
        self.select_ui_actions.append(toolbar.addWidget(self.btn_split))

        self.btn_relax = QPushButton("Relax Provinces")
        self.btn_relax.clicked.connect(self.relax_selected_provinces_func)
        self.select_ui_actions.append(toolbar.addWidget(self.btn_relax))

        # View tool

        self.btn_find = QPushButton("Find Province")
        self.btn_find.clicked.connect(self.find_province_func)
        self.select_view_actions.append(toolbar.addWidget(self.btn_find))

        self.btn_goto = QPushButton("Go to Coords")
        self.btn_goto.clicked.connect(self.goto_coordinates_func)
        self.select_view_actions.append(toolbar.addWidget(self.btn_goto))

        # Initial Update
        self.update_toolbar_visibility()

    def setup_side_panel(self):
        """Creates a Dock Widget on the right for global settings."""
        from PySide6.QtWidgets import QDockWidget, QGroupBox # Ensure these are imported

        dock = QDockWidget("Map", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        content = QWidget()
        layout = QVBoxLayout()
        content.setLayout(layout)

        # --- SECTION 1: VISUALIZATION ---
        vis_group = QGroupBox("Visualization")
        vis_layout = QVBoxLayout()
        vis_group.setLayout(vis_layout)

        vis_layout.addWidget(QLabel("Map Mode:"))
        self.map_mode_combo = QComboBox()
        for name, idx in MAP_MODES:
            self.map_mode_combo.addItem(name, idx)
        self.map_mode_combo.currentIndexChanged.connect(self.trigger_lut_update)
        vis_layout.addWidget(self.map_mode_combo)
        
        self.mix_checkbox = QCheckBox("Mixed Mode")
        self.mix_checkbox.stateChanged.connect(self.trigger_lut_update)
        vis_layout.addWidget(self.mix_checkbox)

        self.overlay_checkbox = QCheckBox("Show Overlay")
        self.overlay_checkbox.stateChanged.connect(self.toggle_overlay)
        vis_layout.addWidget(self.overlay_checkbox)
        
        layout.addWidget(vis_group)

        # --- SECTION 2: FILE OPS ---
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        file_group.setLayout(file_layout)

        # Existing Save Button
        btn_save = QPushButton("Save Bitmap (Overwrite Source)")
        btn_save.setMinimumHeight(40) 
        btn_save.clicked.connect(self.save_map_data)
        file_layout.addWidget(btn_save)

        # --- NEW BUTTON HERE ---
        btn_export = QPushButton("Export View As...")
        btn_export.clicked.connect(self.export_view_map)
        file_layout.addWidget(btn_export)
        # -----------------------

        layout.addWidget(file_group)

        # Add a spacer at the bottom to push everything up
        layout.addStretch()

        dock.setWidget(content)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def change_tool(self, index):
        new_mode = self.tool_combo.currentData()
        self.viewer.current_mode = new_mode
        self.update_toolbar_visibility()
        selected_colors.clear()
        self.trigger_lut_update()
        self.viewer.update_active_cursor()

    def update_toolbar_visibility(self):
        current_mode = self.viewer.current_mode
        show_paint = isinstance(current_mode, PaintMode)
        show_select = isinstance(current_mode, SelectionMode)
        show_view = isinstance(current_mode, ViewMode)

        for action in self.paint_ui_actions:
            action.setVisible(show_paint)

        for action in self.select_ui_actions:
            action.setVisible(show_select)

        for action in self.select_view_actions:
            action.setVisible(show_view)

    # --- ACTION HANDLERS ---

    def open_custom_color_dialog(self):
        # 1. Open dialog with current color as default
        current = self.viewer.current_color
        dialog = SetColorDialog(current, self)
        
        if dialog.exec():
            # 2. Get the QColor object from the dialog
            new_color = dialog.get_color()
            
            # 3. Apply it to the viewer
            # This handles setting the internal state and emitting the signal 
            # that updates the UI display automatically.
            self.viewer.set_active_color(new_color)
            
            # 4. Optional: Switch to Paint Mode automatically for convenience
            idx_paint = self.tool_combo.findText("Painting")
            if idx_paint >= 0:
                self.tool_combo.setCurrentIndex(idx_paint)

    def setup_new_province(self, prov_type):
        """Called when user clicks one of the new buttons."""
        try:
            # 1. Get new color from external logic
            rgb_tuple = get_new_province_color(prov_type)
            
            # 2. Convert tuple to QColor
            new_color = QColor(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
            
            # 3. Set to viewer in 'Creation Mode'
            self.viewer.set_creation_color(new_color)
            
        except Exception as e:
            print(f"Error getting new province color: {e}")

    def create_state_func(self):
        dialog = CreateStateDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            print(f"User confirmed! Running Fill with: {data}")
            state_name = data['state_name']
            state_owner = data['state_owner']
            provs = selected_colors_to_provinces()
            create_new_state(provs, state_name, state_owner)
            selected_colors.clear()
            self.trigger_lut_update()

    def create_strategic_region_func(self):
        dialog = CreateRegionDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            print(f"User confirmed! Running Fill with: {data}")
            region_name = data['region_name']
            provs = selected_colors_to_provinces()
            create_new_strategicregion(provs, region_name)
            selected_colors.clear()
            self.trigger_lut_update()

    def transfer_to_stratregion_func(self):
        dialog = TransferProvsDialog(self, ToStratRegion=True)
        if dialog.exec():
            data = dialog.get_data()
            provs = selected_colors_to_provinces()
            transfer_provinces_to_strategicregion(provs, data['target_state'])
            selected_colors.clear()
            self.trigger_lut_update()

    def transfer_to_state_func(self):
        dialog = TransferProvsDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            provs = selected_colors_to_provinces()
            transfer_provinces_to_state(provs, data['target_state'])
            selected_colors.clear()
            self.trigger_lut_update()

    def edit_province_properties_func(self):
        # 1. Get selected IDs
        provs = selected_colors_to_provinces()
        if not provs:
            print("No provinces selected.")
            return

        # 2. Gather Data (Current State)
        # This handles the "Mixed" logic and Info string
        current_data = get_prov_props(provs)

        # 3. Open the Unified Dialog
        dialog = ProvincePropertiesDialog(current_data, self)
        
        if dialog.exec():
            # 4. Get overrides (only what was checked)
            changes = dialog.get_data()
            
            if changes:
                # 5. Apply changes
                set_prov_props(provs, changes)
                
                # 6. Cleanup
                selected_colors.clear()
                self.trigger_lut_update()
            else:
                print("No changes made.")

    def edit_state_properties_func(self):
        # 1. Get selected IDs (We use provinces to find the states)
        provs = selected_colors_to_provinces()
        if not provs:
            print("No selection to identify states.")
            return

        # 2. Gather Data 
        # You said you will handle these functions, but the flow requires 
        # fetching the data first to populate the dialog.
        try:
            # expected return: {"name": "Texas", "impassable": "no", "info": "State ID: 123..."}
            # or {"name": "-- mixed --", ...} if multiple states selected
            current_data = get_state_props(provs) 
        except NameError:
            print("Backend function 'get_state_props' not found.")
            return

        # 3. Open Dialog
        dialog = StatePropertiesDialog(current_data, self)
        
        if dialog.exec():
            changes = dialog.get_data()
            if changes:
                try:
                    # You implement this: apply 'changes' dict to states belonging to 'provs'
                    set_state_props(provs, changes) 
                    
                    # Cleanup
                    selected_colors.clear()
                    self.trigger_lut_update()
                    print(f"State properties updated: {changes}")
                except NameError:
                    print("Backend function 'set_state_props' not found.")
            else:
                print("No state changes made.")

    def edit_vps_func(self):
        """Edit victory points for the currently selected provinces."""
        provs = selected_colors_to_provinces()
        if not provs:
            print("No provinces selected.")
            return

        try:
            vps = get_victory_points(provs)
        except NameError:
            print("Backend function 'get_victory_points' not found.")
            return

        dialog = VictoryPointsDialog(vps, provs, self)
        if dialog.exec():
            new_vps = dialog.get_vps()
            try:
                set_victory_points(new_vps)
                # Clear selection and refresh visualization so VP map mode updates
                selected_colors.clear()
                self.trigger_lut_update()
                print(f"Victory points updated: {new_vps}")
            except NameError:
                print("Backend function 'set_victory_points' not found.")

    def relax_selected_provinces_func(self):
        # 1. Check selection
        if not selected_colors:
            print("No provinces selected to relax.")
            return

        # --- NEW: Dialog for Settings ---
        dialog = RelaxSettingsDialog(self)
        if not dialog.exec():
            return # User cancelled
        
        # Get values from dialog
        iters, d_scale, d_mag = dialog.get_values()

        # 2. Prepare Data Image as NumPy Array
        img = self.viewer.data_image
        width = img.width()
        height = img.height()
        
        ptr = img.bits()
        # Create a view of the data (H, W, 4). Copying to ensure safety during manipulation.
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4)).copy()

        # 3. Create a Single Mask for ALL selected provinces
        # We need a boolean mask where True = "Any of the selected colors"
        combined_mask = np.zeros((height, width), dtype=bool)
        
        # We slice the first 3 channels (B, G, R) for comparison
        img_bgr = arr[:, :, :3]

        found_any = False
        
        # Build the mask by combining all selected colors
        for color_tuple in selected_colors:
            r, g, b = color_tuple
            # Match channel order (B, G, R)
            target_color = np.array([b, g, r], dtype=np.uint8)
            
            # Check where image matches target
            matches = np.all(img_bgr == target_color, axis=2)
            
            if np.any(matches):
                combined_mask |= matches # Logical OR to add to the group
                found_any = True

        if not found_any:
            print("Selected colors not found in image.")
            return

        print(f"Preparing to relax selection (Iter: {iters}, Scale: {d_scale}, Mag: {d_mag})...")

        # 4. Bounding Box Optimization (Crucial for performance)
        # Find rows and cols that have at least one selected pixel
        rows = np.any(combined_mask, axis=1)
        cols = np.any(combined_mask, axis=0)
        
        # Get indices
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        
        # Add Padding (so the relaxation has room to wiggle at the edges)
        pad = 50 
        y_min = max(0, y_min - pad)
        y_max = min(height, y_max + pad)
        x_min = max(0, x_min - pad)
        x_max = min(width, x_max + pad)

        # 5. Extract Crops (ROI - Region of Interest)
        roi_img = arr[y_min:y_max, x_min:x_max, :3]
        roi_mask = combined_mask[y_min:y_max, x_min:x_max]

        # 6. Run the Relaxation Algorithm
        # Note: We pass the variables collected from the dialog
        print(f"Processing ROI: {x_max-x_min}x{y_max-y_min} pixels...")
        
        relaxed_roi = relax_layer(
            roi_img, 
            mask=roi_mask, 
            iterations=iters, 
            distortion_scale=d_scale, 
            distortion_magnitude=d_mag
        )

        # 7. Write Result back to Main Array
        arr[y_min:y_max, x_min:x_max, :3] = relaxed_roi

        # 8. Update QImage
        new_qimage = QImage(arr.data, width, height, width * 4, QImage.Format_ARGB32).copy()
        
        self.viewer.data_image = new_qimage
        self.viewer.refresh_viewport()

        # --- NEW: Clear Selection after completion ---
        selected_colors.clear()
        self.trigger_lut_update()
        
        print("Relaxation Complete.")

    def split_selected_provinces_func(self):
        # 1. Check selection
        if not selected_colors:
            print("No provinces selected to split.")
            return

        # 2. Prepare Data Image as NumPy Array
        # We use a copy to ensure we don't segfault by messing with QImage memory alignment directly 
        # during complex ops, then we will load it back later.
        img = self.viewer.data_image
        width = img.width()
        height = img.height()
        
        # Get raw data as a NumPy array (H, W, 4) - assuming ARGB32
        # Note: QImage.bits() returns a pointer. We need to be careful with channel order (Usually BGR or RGB).
        ptr = img.bits()
        #ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4)).copy()

        # Determine channel order based on your LUT logic. 
        # Usually PySide QImage Format_ARGB32 is B-G-R-A in byte order on Little Endian.
        # Your code seems to handle this in generate_lut, so check if you need to flip RGB.
        # For this snippet, I will assume the array is [B, G, R, A].

        changes_made = False

        # 3. Iterate over the set of selected colors
        # We iterate a copy of the set because we might modify the selection or colors during the process
        current_selection = list(selected_colors) 

        for color_tuple in current_selection:
            # color_tuple is (R, G, B) from your selection logic
            r, g, b = color_tuple
            
            # Create the target color array for comparison. 
            # CAREFUL: If your array is BGR, this needs to be [b, g, r]
            target_color = np.array([b, g, r], dtype=np.uint8)

            # --- A. FIND PIXELS (The Fast Way) ---
            # Create a boolean mask where the first 3 channels match the target color
            # This scans the whole map in milliseconds.
            mask = np.all(arr[:, :, :3] == target_color, axis=2)
            
            # Get coordinates: argwhere returns array of [y, x]
            # We assume your split function wants [(x,y), (x,y)...]
            coords_y, coords_x = np.where(mask)
            
            # Combine into list of tuples (x, y) for the external function
            # (Zip is standard python but fast enough for this conversion)
            pixel_list = list(zip(coords_x, coords_y))
            
            if not pixel_list:
                continue

            print(f"Splitting province with {len(pixel_list)} pixels...")

            # --- B. SPLIT (External Function) ---
            # Returns two lists. We only need to repaint list_b.
            list_a, list_b = split_pixels_geodesic(pixel_list)

            if not list_b:
                print("Split resulted in empty second province. Skipping.")
                continue

            # --- C. COLOR GENERATION ---
            # Get new color (R, G, B)
            # Note: You might need to determine if it's Land/Sea/Lake based on the old color
            # For now, assuming generic land or passing a type if you have it.
            new_rgb = get_new_province_color("land") 
            new_r, new_g, new_b = new_rgb
            
            # Register the new province definitions
            create_new_province_from(color_tuple, new_rgb)

            # --- D. REPAINT (The Fast Way) ---
            # Convert list_b back to numpy indices (y, x)
            # We unzip the list [(x,y), ...] -> (x_tuple, y_tuple)
            b_xs, b_ys = zip(*list_b)
            
            # Use Advanced Integer Indexing to set color at once
            # Remember: Array is (Y, X) and color is likely BGR
            arr[b_ys, b_xs, 0] = new_b
            arr[b_ys, b_xs, 1] = new_g
            arr[b_ys, b_xs, 2] = new_r
            # arr[..., 3] (Alpha) is likely already 255, but you can set it if needed.

            changes_made = True

        # 4. Write back to QImage
        if changes_made:
            # Construct new QImage from the modified array
            # We must keep a reference to 'arr' or copy it, because QImage references the buffer
            new_qimage = QImage(arr.data, width, height, width * 4, QImage.Format_ARGB32).copy()
            
            self.viewer.data_image = new_qimage
            self.viewer.refresh_viewport()
            print("Split Complete.")

    def find_province_func(self):
        dialog = FindProvinceDialog(self)
        if dialog.exec():
            # 1. Get the color from the dialog (it handles the ID->Color conversion)
            success, rgb = dialog.get_result()

            if not success or rgb is None:
                print("Could not find a definition for that Province ID.")
                return

            r, g, b = rgb
            print(f"Searching for RGB: {r}, {g}, {b}...")

            # 2. Search for the pixel in the image
            coords = self.viewer.find_pixel_by_color(r, g, b)

            if coords:
                x, y = coords
                print(f"Found at {x}, {y}")

                # 3. Select it
                selected_colors.clear()
                selected_colors.add((r, g, b))
                update_composite_lut()
                
                # 4. Pan Camera
                self.viewer.centerOn(x, y)
                self.viewer.refresh_viewport()
            else:
                print(f"Color ({r},{g},{b}) found in CSV, but not on the map bitmap!")

    def goto_coordinates_func(self):
        # Safety check: Is an image loaded?
        if not self.viewer.data_image: 
            print("No map loaded.")
            return

        w = self.viewer.data_image.width()
        h = self.viewer.data_image.height()

        # pass width/height to dialog to set SpinBox limits
        dialog = GoToCoordDialog(w, h, self)
        
        if dialog.exec():
            x, y = dialog.get_coords()
            
            print(f"Panning to {x}, {y}")
            
            # 1. Ensure Minimum Zoom
            # We check the current scale factor (m11). 
            # If it's less than 4x, we reset and zoom in to 8x for precision.
            current_zoom = self.viewer.transform().m11()
            if current_zoom < 4.0:
                self.viewer.resetTransform()
                self.viewer.scale(8.0, 8.0)
            
            # 2. Pan to location
            self.viewer.centerOn(x, y)
            
            # 3. Optional: Add a temporary cursor update or refresh
            self.viewer.update_active_cursor()

    def cycle_tool_mode(self):
        """Cycles through View -> Drawing -> Select -> View..."""
        count = self.tool_combo.count()
        next_index = (self.tool_combo.currentIndex() + 1) % count
        self.tool_combo.setCurrentIndex(next_index)

    def cycle_brush_size(self):
        # Only cycle if we are in Drawing Mode
        if not isinstance(self.viewer.current_mode, PaintMode):
            return

        current_size = self.viewer.brush_size
        
        # Find current index
        try:
            current_index = self.brush_sizes_list.index(current_size)
        except ValueError:
            current_index = 0

        # Calculate next index (wrap around with modulo)
        next_index = (current_index + 1) % len(self.brush_sizes_list)
        new_size = self.brush_sizes_list[next_index]

        # 1. Update the UI (Check the correct button in the toolbar)
        if new_size in self.brush_action_map:
            self.brush_action_map[new_size].setChecked(True)

        # 2. Update the Viewer (Updates brush size and cursor)
        self.viewer.set_brush_size(new_size)

    def trigger_lut_update(self):
        csv_index = self.map_mode_combo.currentData()
        is_mixed = self.mix_checkbox.isChecked()
        global lut
        lut = generate_lut(csv_index, is_mixed)
        self.viewer.refresh_viewport()

    def toggle_overlay(self, state):
        self.viewer.set_overlay_enabled(self.overlay_checkbox.isChecked())

    def update_color_display(self, color):
        pixmap = QPixmap(24, 24)
        
        if color is None:
            # Draw a transparent/checker pattern or just white with '?'
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            # Draw a border
            painter.setPen(Qt.black)
            painter.drawRect(0, 0, 23, 23)
            # Draw a Red X
            painter.setPen(Qt.red)
            painter.drawLine(0, 0, 23, 23)
            painter.drawLine(0, 23, 23, 0)
            painter.end()
        else:
            pixmap.fill(color)
            
        self.color_display.setPixmap(pixmap)

    def save_map_data(self):
        """Saves the underlying data image to the hardcoded path."""
        if self.viewer.data_image and not self.viewer.data_image.isNull():
            # Convert Path object to string for Qt compatibility
            save_path = str(HARDCODED_IMAGE_PATH)
            print(f"Saving map data to: {save_path}...")
            
            # Save the image. Qt infers format from file extension (BMP)
            success = self.viewer.data_image.save(save_path)
            
            if success:
                print("Map saved successfully.")
            else:
                print(f"ERROR: Failed to save map to {save_path}")

    def export_view_map(self):
        """Saves the CURRENT visual display (LUT + Overlay) to a custom file."""
        if not self.viewer.display_image or self.viewer.display_image.isNull():
            print("No image loaded to export.")
            return

        # Open File Dialog asking user where to save
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Current View", 
            "map_view.png", 
            "PNG Images (*.png);;BMP Images (*.bmp);;All Files (*)"
        )

        if file_path:
            # We save the display_image, which contains the visual output
            success = self.viewer.display_image.save(file_path)
            if success:
                print(f"Exported view successfully to: {file_path}")
            else:
                print(f"Failed to export view to: {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())