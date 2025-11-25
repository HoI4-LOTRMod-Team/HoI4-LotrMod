import sys
import os
import numpy as np
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QMainWindow, QToolBar, 
                               QLabel, QWidget, QComboBox, QCheckBox)
from PySide6.QtGui import (QPixmap, QPainter, QImage, QColor, QMouseEvent, 
                           QAction, QActionGroup)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal

# Assuming this exists based on your upload
from definitioncsv import *

# --- CONFIGURATION ---
HARDCODED_IMAGE_PATH = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\provinces - Copy.bmp'

# Your Custom Map Modes
MAP_MODES = [
    ("Province", 8),
    ("Terrain", 9),
    ("Type", 10),
    ("Coastal", 11),
    ("Continent", 12),
    ("State", 14),
    ("Strat Region", 16),
]

# ============================================================
#  GLOBAL LUT CONFIGURATION
# ============================================================

def generate_lut(target_column_index, use_mixed_mode=False):
    """
    Generates a 3D lookup table mapping RGB -> CSV Column Value.
    If use_mixed_mode is True, it blends the target color (80%) 
    with the original province color (20%).
    """
    print(f"Generating LUT (Col: {target_column_index}, Mixed: {use_mixed_mode})...")
    
    # Initialize with identity (Unmapped colors look like the original image)
    lut = np.indices((256, 256, 256), dtype=np.uint8).transpose(1, 2, 3, 0)

    try:
        csv = get_expanded_definition()
        for row in csv:
            # Safety check: ensure the row has enough columns
            if target_column_index < len(row):
                
                # 1. Get Target Color (The Map Mode Color)
                target_val = row[target_column_index]
                
                if hasattr(target_val, '__getitem__') and len(target_val) >= 3:
                    # RGB -> BGR for Qt
                    target_bgr = np.array(target_val[::-1], dtype=np.float32)
                    
                    final_color = target_bgr

                    # 2. Apply Mixing if requested
                    if use_mixed_mode:
                        # Base Color is in row[1] (R), row[2] (G), row[3] (B)
                        # We need BGR format for the math to match target_bgr
                        base_bgr = np.array([row[3], row[2], row[1]], dtype=np.float32)
                        
                        # Blend: 80% Map Mode, 20% Original Province
                        mixed = (target_bgr * 0.65) + (base_bgr * 0.35)
                        final_color = mixed

                    # 3. Assign to LUT
                    # lut indices are [R, G, B]
                    lut[row[1], row[2], row[3]] = final_color.astype(np.uint8)

    except Exception as e:
        print(f"Error generating LUT: {e}")
    
    return lut

# GLOBAL VARIABLE
# Initialize with the first mode in the config
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

class DebugMode(ToolMode):
    def getName(self): return "Debug / Test"

    def _log(self, action, x, y, color):
        c_str = f"R:{color.red()} G:{color.green()} B:{color.blue()}"
        print(f"[DEBUG] {action} at ({x}, {y}) - Color: [{c_str}]")

    def on_left_click(self, view, x, y, color):
        self._log("Left Click", x, y, color)
    def on_left_drag(self, view, x, y, color):
        self._log("Left Drag", x, y, color)
    def on_right_click(self, view, x, y, color):
        self._log("Right Click", x, y, color)
    def on_right_drag(self, view, x, y, color):
        self._log("Right Drag", x, y, color)
    def on_shift_click(self, view, x, y, color):
        self._log("Shift + Click", x, y, color)
    def on_alt_click(self, view, x, y, color):
        self._log("Alt + Click", x, y, color)


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

    def refresh_viewport(self):
        """Re-runs the LUT over the entire image and updates the scene."""
        if not self.data_image: return
        self.update_display() # Runs the LUT over the whole image
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

        # 2. Update Display with LUT
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

        # ----------------------------------------------------
        # LUT OPERATION
        # ----------------------------------------------------
        b_indices = arr_data[y1:y2, x1:x2, 0]
        g_indices = arr_data[y1:y2, x1:x2, 1]
        r_indices = arr_data[y1:y2, x1:x2, 2]

        arr_display[y1:y2, x1:x2, 3] = arr_data[y1:y2, x1:x2, 3]
        arr_display[y1:y2, x1:x2, 0:3] = lut[r_indices, g_indices, b_indices]


    # --- IMAGE LOADING ---

    def load_image(self, path):
        if not os.path.exists(path):
            print(f"Error: {path}")
            return

        img = QImage(path)
        if img.isNull(): return
        
        self.data_image = img.convertToFormat(QImage.Format_ARGB32)
        self.display_image = QImage(self.data_image.size(), QImage.Format_ARGB32)

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

        self.viewer = EditorView()
        self.setCentralWidget(self.viewer)
        self.viewer.colorChanged.connect(self.update_color_display)
        
        self.setup_toolbar()
        
        self.viewer.load_image(HARDCODED_IMAGE_PATH)
        self.viewer.emit_current_color()

    def setup_toolbar(self):
        toolbar = QToolBar("Tools")
        self.addToolBar(toolbar)

        # --- MODE SELECTOR ---
        toolbar.addWidget(QLabel("Map Mode: "))
        self.map_mode_combo = QComboBox()
        # Populate based on Configuration
        for name, idx in MAP_MODES:
            self.map_mode_combo.addItem(name, idx)
        
        self.map_mode_combo.currentIndexChanged.connect(self.trigger_lut_update)
        toolbar.addWidget(self.map_mode_combo)
        
        # --- MIX CHECKBOX ---
        self.mix_checkbox = QCheckBox("Mixed")
        self.mix_checkbox.stateChanged.connect(self.trigger_lut_update)
        toolbar.addWidget(self.mix_checkbox)

        toolbar.addSeparator()

        # --- TOOL SELECTOR ---
        toolbar.addWidget(QLabel("Tool: "))
        self.tool_combo = QComboBox()
        self.tool_combo.addItem("Drawing", PaintMode())
        self.tool_combo.addItem("Debug", DebugMode())
        self.tool_combo.currentIndexChanged.connect(self.change_tool)
        toolbar.addWidget(self.tool_combo)
        
        toolbar.addSeparator()

        toolbar.addWidget(QLabel(" Color: "))
        self.color_display = QLabel()
        self.color_display.setFixedSize(24, 24)
        self.color_display.setStyleSheet("border: 1px solid #555;") 
        toolbar.addWidget(self.color_display)
        
        toolbar.addSeparator()

        toolbar.addWidget(QLabel(" Size: "))
        brush_group = QActionGroup(self)
        sizes = [("1px", 1), ("3px", 3), ("5px", 5), ("10px", 10), ("20px", 20)]

        for label, size in sizes:
            action = QAction(label, self)
            action.setCheckable(True)
            if size == 10:
                action.setChecked(True)
                self.viewer.brush_size = size
            action.triggered.connect(lambda c, s=size: setattr(self.viewer, 'brush_size', s))
            brush_group.addAction(action)
            toolbar.addAction(action)

    def trigger_lut_update(self):
        """Unified handler for Combo Box or Checkbox changes"""
        # 1. Get Settings
        csv_index = self.map_mode_combo.currentData()
        is_mixed = self.mix_checkbox.isChecked()

        # 2. Update Global LUT
        global lut
        lut = generate_lut(csv_index, is_mixed)
        
        # 3. Refresh View
        self.viewer.refresh_viewport()

    def change_tool(self, index):
        new_mode = self.tool_combo.currentData()
        self.viewer.current_mode = new_mode

    def update_color_display(self, color):
        pixmap = QPixmap(24, 24)
        pixmap.fill(color)
        self.color_display.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())