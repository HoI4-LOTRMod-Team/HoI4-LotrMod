import sys
import os
import numpy as np
import random # Imported for the dummy color generator
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QMainWindow, QToolBar, 
                               QLabel, QWidget, QComboBox, QCheckBox, 
                               QPushButton, QDialog, QFormLayout, QDialogButtonBox,
                               QVBoxLayout, QSpinBox, QLineEdit, QHBoxLayout, QTextEdit)
from PySide6.QtGui import (QPixmap, QPainter, QImage, QColor, QMouseEvent, 
                           QAction, QActionGroup)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal

# --- IMPORT PILLOW (Robust DDS Support) ---
try:
    from PIL import Image
except ImportError:
    print("CRITICAL: Pillow not found. Run 'pip install Pillow' to fix DDS loading.")

# Assuming this exists based on your upload
from definitioncsv import *


# --- CONFIGURATION ---
BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve() 
HARDCODED_IMAGE_PATH = BASE_PATH / "map" / "provinces - Copy.bmp"
OVERLAY_PATH = BASE_PATH / "map" / "terrain" / "colormap_rgb_cityemissivemask_a.dds"

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
                        mixed = (target_bgr * 0.65) + (base_bgr * 0.35)
                        final_color = mixed

                    # row[1]=R, row[2]=G, row[3]=B
                    base_lut[row[1], row[2], row[3]] = final_color.astype(np.uint8)
    except Exception as e:
        print(f"Error generating LUT: {e}")
    
    # After generating base, rebuild the active LUT (to keep selection if any)
    update_composite_lut()
    return lut

lut = generate_lut(MAP_MODES[0][1], False)


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
    def getName(self): return "Selection"
    # ... (Selection logic remains unchanged) ...
    def _update_selection(self, view, x, y, color, keep_existing=False):
        global selected_colors
        rgb_key = (color.red(), color.green(), color.blue())
        if not keep_existing:
            selected_colors.clear()
        selected_colors.add(rgb_key)
        update_composite_lut()
        radius = 300
        update_rect = QRectF(x - radius, y - radius, radius * 2, radius * 2)
        view.refresh_viewport(update_rect)

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
        view.refresh_viewport()

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
        layout.addLayout(form_layout)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept) 
        self.buttons.rejected.connect(self.reject) 
        layout.addWidget(self.buttons)

    def get_data(self):
        return {"state_name": self.name_input.text()}
    
class TransferProvsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transfer Provinces")
        self.setModal(True)
        self.setMinimumWidth(300)
        layout = QVBoxLayout()
        self.setLayout(layout)
        states = get_all_states()
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
            av_st_id = str(av_st.state_id)
            av_st_name = state_loc.get(str(av_st.pObj.GetVal("name")).replace('"', ''))
            if av_st_name is None: av_st_name = ""
            self.available_states.addItem(av_st_id + "  " + av_st_name, av_st.state_id)
        form_layout.addRow("Target:", self.available_states)
        layout.addLayout(form_layout)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept) 
        self.buttons.rejected.connect(self.reject) 
        layout.addWidget(self.buttons)

    def get_data(self):
        return {"target_state": self.available_states.currentData()}

class ProvincePropertiesDialog(QDialog):
    # --- CONFIGURATION: EDIT OPTIONS HERE ---
    PROPERTIES_CONFIG = {
        "type":      ["land", "sea", "lake"],
        "coastal":   ["true", "false"],
        "terrain":   [
            "unknown",
            "ocean",
            "lakes",
            "forest",
            "hills",
            "mountain",
            "plains",
            "dark_grounds",
            "urban",
            "jungle",
            "marsh",
            "desert",
            "water_fjords",
            "water_shallow_sea",
            "water_deep_ocean",
        ],
        "continent": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Province Properties")
        self.setModal(True)
        self.setMinimumWidth(350)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Dictionary to store widget references: {"Type": (checkbox, combobox), ...}
        self.widgets = {}

        # Generate rows based on the configuration
        for name, options in self.PROPERTIES_CONFIG.items():
            row_layout = QHBoxLayout()
            
            # The Checkbox (Enable/Disable property)
            chk = QCheckBox(name)
            chk.setChecked(False)
            
            # The Dropdown
            combo = QComboBox()
            combo.addItems(options)
            combo.setEnabled(False) # Disabled by default
            
            # Logic: Disable combo if checkbox is unchecked
            chk.toggled.connect(combo.setEnabled)

            # Add to layout
            row_layout.addWidget(chk)
            row_layout.addWidget(combo)
            self.layout.addLayout(row_layout)
            
            # Store reference
            self.widgets[name] = (chk, combo)

        # Standard Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        """
        Returns a dict of properties to change.
        Format: {'Type': 'Land', 'Terrain': 'Forest'} 
        Only includes keys where the checkbox was checked.
        """
        result = {}
        for name, (chk, combo) in self.widgets.items():
            if chk.isChecked():
                result[name] = combo.currentText()
        return result
    
class ProvincePropertiesDialog(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Province Properties")
        self.setModal(True)
        self.resize(400, 300) # Give it a reasonable default size
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Read-only text area to show the properties
        self.text_area = QTextEdit()
        self.text_area.setPlainText(text)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # Simple Close button
        self.buttons = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttons.rejected.connect(self.reject) 
        layout.addWidget(self.buttons)


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

        self.current_color = QColor(255, 0, 0)
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
        self.current_color = color
        self.pending_province_creation = True # Next paint will trigger logic
        self.colorChanged.emit(self.current_color)
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

        # --- NEW PROVINCE LOGIC ---
        # If specific button was clicked, logic triggers on FIRST paint event
        if self.pending_province_creation:
            # 1. Get the color CURRENTLY at this pixel (the one we are about to overwrite)
            if 0 <= x < self.data_image.width() and 0 <= y < self.data_image.height():
                old_qt_color = self.data_image.pixelColor(x, y)
                old_rgb = (old_qt_color.red(), old_qt_color.green(), old_qt_color.blue())
                new_rgb = (self.current_color.red(), self.current_color.green(), self.current_color.blue())
                
                # 2. Call external function
                create_new_province_from(old_rgb, new_rgb)
            
            # 3. Disable flag so it doesn't trigger again while dragging
            self.pending_province_creation = False


        # 1. Modify Data
        painter = QPainter(self.data_image)
        painter.setBrush(self.current_color)
        painter.setPen(Qt.NoPen)
        painter.setRenderHint(QPainter.Antialiasing, False) 

        offset = self.brush_size / 2.0
        dirty_rect = QRectF(x - offset, y - offset, float(self.brush_size), float(self.brush_size))
        
        if self.brush_size == 1:
            painter.setPen(self.current_color)
            painter.drawPoint(x, y)
        else:
            painter.drawEllipse(dirty_rect)
        painter.end()

        # 2. Update Display
        safe_rect = dirty_rect.adjusted(-1, -1, 1, 1)
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
            if img.size != (width, height):
                img = img.resize((width, height), Image.Resampling.NEAREST)
            img = img.convert("RGBA")
            arr = np.array(img)
            raw_alpha = arr[:, :, 3].astype(np.float32) / 255.0
            brightness_factor = 2.0 
            self.overlay_alpha_map = np.clip(raw_alpha * brightness_factor, 0.0, 1.0)
            print("Overlay loaded and cached successfully.")
        except Exception as e:
            print(f"FAILED to load DDS via Pillow: {e}")

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

# ============================================================
#  MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Editor - LUT Shader")
        self.resize(1000, 700)

        self.paint_ui_actions = []
        self.select_ui_actions = []

        self.viewer = EditorView()
        self.setCentralWidget(self.viewer)
        self.viewer.colorChanged.connect(self.update_color_display)
        
        self.setup_toolbar()
        self.update_toolbar_visibility()

        self.viewer.load_image(HARDCODED_IMAGE_PATH)
        self.viewer.emit_current_color()

    def setup_toolbar(self):
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)

        btn_save = QPushButton("Save Map")
        btn_save.clicked.connect(self.save_map_data)
        toolbar.addWidget(btn_save)
        
        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Map Mode: "))
        self.map_mode_combo = QComboBox()
        for name, idx in MAP_MODES:
            self.map_mode_combo.addItem(name, idx)
        self.map_mode_combo.currentIndexChanged.connect(self.trigger_lut_update)
        toolbar.addWidget(self.map_mode_combo)
        
        self.mix_checkbox = QCheckBox("Mixed")
        self.mix_checkbox.stateChanged.connect(self.trigger_lut_update)
        toolbar.addWidget(self.mix_checkbox)

        self.overlay_checkbox = QCheckBox("Overlay")
        self.overlay_checkbox.stateChanged.connect(self.toggle_overlay)
        toolbar.addWidget(self.overlay_checkbox)

        toolbar.addSeparator()

        toolbar.addWidget(QLabel("Tool: "))
        self.tool_combo = QComboBox()
        self.tool_combo.addItem("Drawing", PaintMode())
        self.tool_combo.addItem("Select", SelectionMode()) 
        self.tool_combo.currentIndexChanged.connect(self.change_tool)
        toolbar.addWidget(self.tool_combo)
        
        toolbar.addSeparator()

        # ==========================================
        #  PAINTING TOOLS (Modified)
        # ==========================================
        
        # 1. New Buttons for Creation
        # Using lambda default arguments to capture the string
        btn_land = QPushButton("New Land")
        btn_land.clicked.connect(lambda checked=False: self.setup_new_province("land"))
        act = toolbar.addWidget(btn_land)
        self.paint_ui_actions.append(act)

        btn_lake = QPushButton("New Lake")
        btn_lake.clicked.connect(lambda checked=False: self.setup_new_province("lake"))
        act = toolbar.addWidget(btn_lake)
        self.paint_ui_actions.append(act)

        btn_sea = QPushButton("New Sea")
        btn_sea.clicked.connect(lambda checked=False: self.setup_new_province("sea"))
        act = toolbar.addWidget(btn_sea)
        self.paint_ui_actions.append(act)

        toolbar.addSeparator()

        # 2. Standard Paint UI
        act = toolbar.addWidget(QLabel(" Color: "))
        self.paint_ui_actions.append(act)

        self.color_display = QLabel()
        self.color_display.setFixedSize(24, 24)
        self.color_display.setStyleSheet("border: 1px solid #555;") 
        act = toolbar.addWidget(self.color_display)
        self.paint_ui_actions.append(act)
        
        act = toolbar.addWidget(QLabel(" Size: "))
        self.paint_ui_actions.append(act)

        brush_group = QActionGroup(self)
        sizes = [("1px", 1), ("2px", 2), ("4px", 4), ("6px", 6), ("10px", 10)]

        for label, size in sizes:
            action = QAction(label, self)
            action.setCheckable(True)
            if size == 10:
                action.setChecked(True)
                self.viewer.brush_size = size
            action.triggered.connect(lambda c, s=size: setattr(self.viewer, 'brush_size', s))
            brush_group.addAction(action)
            toolbar.addAction(action)
            self.paint_ui_actions.append(action)

        # ==========================================
        #  SELECTION TOOLS
        # ==========================================

        self.btn_action1 = QPushButton("Create State")
        self.btn_action1.clicked.connect(self.create_state_func)
        act = toolbar.addWidget(self.btn_action1)
        self.select_ui_actions.append(act)

        self.btn_action2 = QPushButton("Transfer to State")
        self.btn_action2.clicked.connect(self.transfer_to_state_func)
        act = toolbar.addWidget(self.btn_action2)
        self.select_ui_actions.append(act)

        self.btn_action3 = QPushButton("Set Properties")
        self.btn_action3.clicked.connect(self.set_properties_func)
        act = toolbar.addWidget(self.btn_action3)
        self.select_ui_actions.append(act)

        self.btn_props = QPushButton("Show Properties")
        self.btn_props.clicked.connect(self.show_props_func)
        act = toolbar.addWidget(self.btn_props)
        self.select_ui_actions.append(act)

    def change_tool(self, index):
        new_mode = self.tool_combo.currentData()
        self.viewer.current_mode = new_mode
        self.update_toolbar_visibility()
        selected_colors.clear()
        self.trigger_lut_update()

    def update_toolbar_visibility(self):
        current_mode = self.viewer.current_mode
        show_paint = isinstance(current_mode, PaintMode)
        show_select = isinstance(current_mode, SelectionMode)

        for action in self.paint_ui_actions:
            action.setVisible(show_paint)

        for action in self.select_ui_actions:
            action.setVisible(show_select)

    # --- ACTION HANDLERS ---

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
            provs = selected_colors_to_provinces()
            create_new_state(provs, state_name)
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

    def set_properties_func(self):
        # 1. Check if we actually have a selection
        provs = selected_colors_to_provinces()
        if not provs:
            print("No provinces selected.")
            return

        # 2. Open the Dialog
        dialog = ProvincePropertiesDialog(self)
        if dialog.exec():
            # 3. Get the data (only checked items)
            data = dialog.get_data()
            
            if data:
                # 4. Call your external logic
                update_province_properties(provs, data)
                
                # 5. Cleanup (Optional: clear selection after apply)
                selected_colors.clear()
                self.trigger_lut_update()
            else:
                print("No properties selected to update.")

    def show_props_func(self):
        # 1. Get selected IDs
        provs = selected_colors_to_provinces()
        
        # 2. Call the external function
        text_content = get_province_property_text(provs)
        
        # 3. Show Dialog
        dialog = ProvincePropertiesDialog(text_content, self)
        dialog.exec()

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())