import sys
import os
import numpy as np
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QMainWindow, QToolBar, 
                               QLabel, QWidget, QComboBox, QCheckBox, 
                               QPushButton, QDialog, QFormLayout, QDialogButtonBox,
                               QVBoxLayout, QSpinBox, QLineEdit)
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
HARDCODED_IMAGE_PATH = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\provinces - Copy.bmp'
OVERLAY_PATH = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\terrain\colormap_rgb_cityemissivemask_a.dds'

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
]

# ============================================================
#  GLOBAL LUT CONFIGURATION
# ============================================================

# We store the "Base" LUT (Map Mode colors) separately from the "Active" LUT (Base + Selection)
base_lut = np.indices((256, 256, 256), dtype=np.uint8).transpose(1, 2, 3, 0)
lut = base_lut.copy()
selected_colors = set() # Stores tuples of (r, g, b)

def selected_colors_to_provinces():
    ret = []
    csv = get_definition_csv()
    for row in csv:
        col = (row[1], row[2], row[3])
        if col in selected_colors:
            ret.append(row[0])
    return ret

def update_composite_lut():
    """
    Copies the Base LUT and applies the Pure Red selection overlay.
    """
    global lut, base_lut, selected_colors
    
    # 1. Start with the clean map mode colors
    lut = base_lut.copy()
    
    # 2. Overwrite selected colors with Pure Red [0, 0, 255] (BGR format for QImage)
    if selected_colors:
        for (r, g, b) in selected_colors:
            # Safety check for valid colors
            if 0 <= r < 256 and 0 <= g < 256 and 0 <= b < 256:
                lut[r, g, b] = [0, 0, 255]

def generate_lut(target_column_index, use_mixed_mode=False):
    """
    Generates the BASE lookup table from CSV.
    """
    print(f"Generating Base LUT (Col: {target_column_index}, Mixed: {use_mixed_mode})...")
    
    global base_lut
    # Reset base
    base_lut = np.indices((256, 256, 256), dtype=np.uint8).transpose(1, 2, 3, 0)

    try:
        csv = get_expanded_definition()
        for row in csv:
            if target_column_index < len(row):
                target_val = row[target_column_index]
                
                if hasattr(target_val, '__getitem__') and len(target_val) >= 3:
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

# Initialize with defaults
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

    def _update_selection(self, view, x, y, color, keep_existing=False):
        global selected_colors
        
        # Color from input is QColor, we need (r, g, b) tuple
        rgb_key = (color.red(), color.green(), color.blue())
        
        print(f"Selecting Color: {rgb_key}")

        if not keep_existing:
            selected_colors.clear()
        
        # Add to selection
        selected_colors.add(rgb_key)

        # Update the global lookup table with red values
        update_composite_lut()

        # Optimize: Only refresh a 300px radius around the click
        radius = 300
        # QRectF(x, y, w, h) - centered on click
        update_rect = QRectF(x - radius, y - radius, radius * 2, radius * 2)
        
        view.refresh_viewport(update_rect)

    def on_left_click(self, view, x, y, color):
        # Single Select
        self._update_selection(view, x, y, color, keep_existing=False)

    def on_left_drag(self, view, x, y, color):
        # Single Select
        self._update_selection(view, x, y, color, keep_existing=True)

    def on_shift_click(self, view, x, y, color):
        # Multi Select
        self._update_selection(view, x, y, color, keep_existing=True)

    def on_right_click(self, view, x, y, color):
        # Clear Selection
        global selected_colors
        selected_colors.clear()
        update_composite_lut()
        view.refresh_viewport() # Full refresh to clear everything

# ============================================================
#  DIALOGUE FORMS
# ============================================================

class CreateStateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create State")
        self.setModal(True) # Blocks parent window until closed
        self.setMinimumWidth(300)

        # 1. Main Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 2. Form Layout for Inputs
        form_layout = QFormLayout()
        
        # -- Example Input: Number (e.g., Expansion radius) --
        #self.radius_input = QSpinBox()
        #self.radius_input.setRange(0, 100)
        #self.radius_input.setValue(10)
        #form_layout.addRow("Expand Selection (px):", self.radius_input)

        # -- Example Input: Text (e.g., ID or Name) --
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Minas Tirith")
        form_layout.addRow("State Name:", self.name_input)

        # -- Example Input: Checkbox --
        #self.force_check = QCheckBox("Force Overwrite")
        #form_layout.addRow("Mode:", self.force_check)

        layout.addLayout(form_layout)

        # 3. Standard Buttons (OK / Cancel)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept) # Closes dialog with result code 1
        self.buttons.rejected.connect(self.reject) # Closes dialog with result code 0
        layout.addWidget(self.buttons)

    def get_data(self):
        """Helper to return all data as a dictionary"""
        return {
            "state_name": self.name_input.text(),
            #"tag": self.tag_input.text(),
            #"overwrite": self.force_check.isChecked()
        }
    
class TransferProvsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transfer Provinces")
        self.setModal(True) # Blocks parent window until closed
        self.setMinimumWidth(300)

        # 1. Main Layout
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

        # 2. Form Layout for Inputs
        form_layout = QFormLayout()
        
        # -- Example Input: Number (e.g., Expansion radius) --
        self.available_states = QComboBox()
        for av_st in av_states:
            self.available_states.addItem(str(av_st.state_id) + "  " + state_loc.get(str(av_st.pObj.GetVal("name")).replace('"', '')))
        form_layout.addRow("Target:", self.available_states)
        #self.available_states.addItem()

        # -- Example Input: Checkbox --
        #self.force_check = QCheckBox("Force Overwrite")
        #form_layout.addRow("Mode:", self.force_check)

        layout.addLayout(form_layout)

        # 3. Standard Buttons (OK / Cancel)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept) # Closes dialog with result code 1
        self.buttons.rejected.connect(self.reject) # Closes dialog with result code 0
        layout.addWidget(self.buttons)

    def get_data(self):
        """Helper to return all data as a dictionary"""
        return {
            "target_state": self.available_states.currentText(),
            #"overwrite": self.force_check.isChecked()
        }


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
        self.current_color = color
        self.colorChanged.emit(self.current_color)
        print(f"Color Picked: {color.name()}")

    def set_overlay_enabled(self, enabled):
        self.use_overlay = enabled
        self.refresh_viewport()

    def refresh_viewport(self, rect=None):
        """Re-runs the LUT and Overlay. If rect is provided, only updates that area."""
        if not self.data_image: return
        self.update_display(rect) 
        self.image_item.setPixmap(QPixmap.fromImage(self.display_image))

    def perform_paint(self, x, y):
        if not self.data_image: return

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

    # --- LUT / SHADER LOGIC ---

    def _qimage_to_numpy(self, image):
        width = image.width()
        height = image.height()
        ptr = image.bits()
        arr = np.frombuffer(ptr, np.uint8).reshape((height, -1))
        return arr[:, :width * 4].reshape((height, width, 4))

    def update_display(self, rect=None):
        if not self.data_image or not self.display_image: return

        # Get Views
        arr_data = self._qimage_to_numpy(self.data_image)
        arr_display = self._qimage_to_numpy(self.display_image)

        # Determine Slice
        if rect:
            x1 = max(0, int(rect.left()))
            y1 = max(0, int(rect.top()))
            x2 = min(self.data_image.width(), int(rect.right()) + 1)
            y2 = min(self.data_image.height(), int(rect.bottom()) + 1)
        else:
            x1, y1 = 0, 0
            x2, y2 = self.data_image.width(), self.data_image.height()

        if x1 >= x2 or y1 >= y2: return

        # 1. APPLY LUT
        b_indices = arr_data[y1:y2, x1:x2, 0]
        g_indices = arr_data[y1:y2, x1:x2, 1]
        r_indices = arr_data[y1:y2, x1:x2, 2]

        arr_display[y1:y2, x1:x2, 3] = arr_data[y1:y2, x1:x2, 3]
        
        # Note: lut uses [r, g, b] indices to output [B, G, R] color
        arr_display[y1:y2, x1:x2, 0:3] = lut[r_indices, g_indices, b_indices]

        # 2. APPLY OVERLAY (MULTIPLY)
        if self.use_overlay and self.overlay_alpha_map is not None:
            # Safe slice logic to handle potential floating point mismatch in rect
            map_h, map_w = self.overlay_alpha_map.shape
            
            # Ensure we don't go out of bounds of the overlay
            safe_x2 = min(x2, map_w)
            safe_y2 = min(y2, map_h)

            if safe_x2 > x1 and safe_y2 > y1:
                alpha_slice = self.overlay_alpha_map[y1:safe_y2, x1:safe_x2]
                alpha_factor = alpha_slice[:, :, np.newaxis]

                current_rgb = arr_display[y1:safe_y2, x1:safe_x2, 0:3].astype(np.float32)
                blended_rgb = current_rgb * alpha_factor
                arr_display[y1:safe_y2, x1:safe_x2, 0:3] = blended_rgb.astype(np.uint8)

    # --- IMAGE LOADING ---

    def _load_overlay(self, width, height):
        """Loads the overlay using Pillow (PIL) for better DDS support."""
        if not os.path.exists(OVERLAY_PATH):
            print(f"Overlay not found at: {OVERLAY_PATH}")
            return

        print("Loading Overlay DDS via Pillow...")
        try:
            # Pillow handles standard and compressed DDS (DXT1/3/5) natively
            img = Image.open(OVERLAY_PATH)
            
            # Ensure size matches the map. Resize if necessary.
            if img.size != (width, height):
                print(f"Warning: Overlay size {img.size} != Map size {(width, height)}. Resizing...")
                img = img.resize((width, height), Image.Resampling.NEAREST)
            
            # Force RGBA
            img = img.convert("RGBA")
            
            # Convert to Numpy
            arr = np.array(img)
            raw_alpha = arr[:, :, 3].astype(np.float32) / 255.0
            
            # Extract Alpha (Index 3) and normalize to 0.0-1.0
            brightness_factor = 2.0 
            self.overlay_alpha_map = np.clip(raw_alpha * brightness_factor, 0.0, 1.0)
            print("Overlay loaded and cached successfully.")
            
        except Exception as e:
            print(f"FAILED to load DDS via Pillow: {e}")
            print("Make sure you have installed Pillow: 'pip install Pillow'")


    def load_image(self, path):
        if not os.path.exists(path):
            print(f"Error: {path}")
            return

        img = QImage(path)
        if img.isNull(): return
        
        self.data_image = img.convertToFormat(QImage.Format_ARGB32)
        self.display_image = QImage(self.data_image.size(), QImage.Format_ARGB32)

        # Attempt to load overlay matching these dimensions
        self._load_overlay(self.data_image.width(), self.data_image.height())

        self.update_display() # Full pass

        pixmap = QPixmap.fromImage(self.display_image)
        self._scene.clear()
        self.image_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self.image_item)
        self.setSceneRect(self.image_item.boundingRect())

    # --- INPUT ROUTING ---

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

        # Lists to store toolbar actions for toggling visibility
        self.paint_ui_actions = []
        self.select_ui_actions = []

        self.viewer = EditorView()
        self.setCentralWidget(self.viewer)
        self.viewer.colorChanged.connect(self.update_color_display)
        
        self.setup_toolbar()
        
        # Initialize visibility based on default tool
        self.update_toolbar_visibility()

        self.viewer.load_image(HARDCODED_IMAGE_PATH)
        self.viewer.emit_current_color()

    def setup_toolbar(self):
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)

        # --- MODE SELECTOR (Always Visible) ---
        toolbar.addWidget(QLabel("Map Mode: "))
        self.map_mode_combo = QComboBox()
        for name, idx in MAP_MODES:
            self.map_mode_combo.addItem(name, idx)
        
        self.map_mode_combo.currentIndexChanged.connect(self.trigger_lut_update)
        toolbar.addWidget(self.map_mode_combo)
        
        # --- MIX CHECKBOX (Always Visible) ---
        self.mix_checkbox = QCheckBox("Mixed")
        self.mix_checkbox.stateChanged.connect(self.trigger_lut_update)
        toolbar.addWidget(self.mix_checkbox)

        # --- OVERLAY CHECKBOX (Always Visible) ---
        self.overlay_checkbox = QCheckBox("Overlay")
        self.overlay_checkbox.stateChanged.connect(self.toggle_overlay)
        toolbar.addWidget(self.overlay_checkbox)

        toolbar.addSeparator()

        # --- TOOL SELECTOR (Always Visible) ---
        toolbar.addWidget(QLabel("Tool: "))
        self.tool_combo = QComboBox()
        self.tool_combo.addItem("Drawing", PaintMode())
        self.tool_combo.addItem("Select", SelectionMode()) 
        self.tool_combo.currentIndexChanged.connect(self.change_tool)
        toolbar.addWidget(self.tool_combo)
        
        toolbar.addSeparator()

        # ==========================================
        #  DYNAMIC: PAINTING TOOLS
        # ==========================================
        
        # Note: toolbar.addWidget returns a QAction. We store that QAction to hide it later.

        # 1. Color Label
        act = toolbar.addWidget(QLabel(" Color: "))
        self.paint_ui_actions.append(act)

        # 2. Color Display Box
        self.color_display = QLabel()
        self.color_display.setFixedSize(24, 24)
        self.color_display.setStyleSheet("border: 1px solid #555;") 
        act = toolbar.addWidget(self.color_display)
        self.paint_ui_actions.append(act)
        
        # 3. Size Label
        act = toolbar.addWidget(QLabel(" Size: "))
        self.paint_ui_actions.append(act)

        # 4. Brush Size Buttons
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
            
            # Add the action to our list so we can hide it
            self.paint_ui_actions.append(action)

        # ==========================================
        #  DYNAMIC: SELECTION TOOLS
        # ==========================================

        # Custom Button 1
        self.btn_action1 = QPushButton("Create State")
        self.btn_action1.clicked.connect(self.create_state_func)
        act = toolbar.addWidget(self.btn_action1)
        self.select_ui_actions.append(act)

        # Custom Button 2
        self.btn_action2 = QPushButton("Transfer to State")
        self.btn_action2.clicked.connect(self.transfer_to_state_func)
        act = toolbar.addWidget(self.btn_action2)
        self.select_ui_actions.append(act)

    def change_tool(self, index):
        new_mode = self.tool_combo.currentData()
        self.viewer.current_mode = new_mode
        self.update_toolbar_visibility()

    def update_toolbar_visibility(self):
        """Hides/Shows toolbar items based on the current mode."""
        current_mode = self.viewer.current_mode
        
        # Determine which set to show
        show_paint = isinstance(current_mode, PaintMode)
        show_select = isinstance(current_mode, SelectionMode)

        for action in self.paint_ui_actions:
            action.setVisible(show_paint)

        for action in self.select_ui_actions:
            action.setVisible(show_select)

    # --- CUSTOM FUNCTION STUBS ---
    def create_state_func(self):
        dialog = CreateStateDialog(self)
        
        # 2. Show the dialog and wait for result (exec() blocks execution)
        if dialog.exec():
            # 3. If User clicked "OK", get the data
            data = dialog.get_data()
            print(f"User confirmed! Running Fill with: {data}")
            
            # Example: Access specific values
            state_name = data['state_name']

            # create list of selected provinces (from selected colors)
            provs = selected_colors_to_provinces()
            
            create_new_state(provs, state_name)
            
        else:
            print("User cancelled.")

    def transfer_to_state_func(self):
        # You can reuse the same dialog class or create a different one
        dialog = TransferProvsDialog(self)

        if dialog.exec():
            data = dialog.get_data()
            print(f"Exporting with: {data}")

            provs = selected_colors_to_provinces()
            transfer_provinces_to_state(provs, data['target_state'])

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())