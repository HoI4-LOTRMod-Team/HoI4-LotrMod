import sys
import os
import numpy as np
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QMainWindow, QToolBar, 
                               QLabel, QWidget, QComboBox)
from PySide6.QtGui import (QPixmap, QPainter, QImage, QColor, QMouseEvent, 
                           QAction, QActionGroup)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal

# --- CONFIGURATION ---
HARDCODED_IMAGE_PATH = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\provinces - Copy.bmp'
# ---------------------

# ============================================================
#  MODE SYSTEM (STRATEGY PATTERN)
# ============================================================

class ToolMode:
    """Base class for all interaction modes"""
    def getName(self): return "Base"

    # All methods receive: view (the editor instance), x, y, and color (QColor of the pixel)
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
        # Helper to print formatting
        c_str = f"R:{color.red()} G:{color.green()} B:{color.blue()}"
        print(f"[DEBUG] {action} at ({x}, {y}) - Color: [{c_str}]")

    def on_left_click(self, view, x, y, color):
        self._log("Left Click", x, y, color)

    def on_left_drag(self, view, x, y, color):
        self._log("Left Drag (Hold)", x, y, color)

    def on_right_click(self, view, x, y, color):
        self._log("Right Click", x, y, color)

    def on_right_drag(self, view, x, y, color):
        self._log("Right Drag (Hold)", x, y, color)

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

        # Core Data
        self.data_image = None 
        self.display_image = None
        self.image_item = None
        
        # Settings
        self.current_color = QColor(255, 0, 0)
        self.brush_size = 10
        self.current_mode = PaintMode() # Default Mode

        # State flags
        self._is_panning = False
        self._last_pan_pos = QPointF()

        # UI Config
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing, False)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    # --- API FOR MODES ---

    def emit_current_color(self):
        self.colorChanged.emit(self.current_color)
    
    def set_active_color(self, color):
        self.current_color = color
        self.colorChanged.emit(self.current_color)
        print(f"Color Picked: {color.name()}")

    

    def perform_paint(self, x, y):
        """Used by DrawingMode to apply paint"""
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

        # 2. Update Display (Shader)
        safe_rect = dirty_rect.adjusted(-1, -1, 1, 1)
        self.apply_shader_to_rect(safe_rect)
        self.image_item.setPixmap(QPixmap.fromImage(self.display_image))

    # --- SHADER LOGIC ---

    def apply_shader_numpy(self):
        width = self.data_image.width()
        height = self.data_image.height()

        ptr_data = self.data_image.constBits()
        arr_data = np.frombuffer(ptr_data, np.uint8).reshape((height, -1))
        arr_data = arr_data[:, :width * 4].reshape((height, width, 4))

        ptr_display = self.display_image.bits()
        arr_display = np.frombuffer(ptr_display, np.uint8).reshape((height, -1))
        arr_display = arr_display[:, :width * 4].reshape((height, width, 4))

        # Shader: Swap Red and Green
        arr_display[:, :, 3] = arr_data[:, :, 3] # Alpha
        arr_display[:, :, 0] = arr_data[:, :, 0] # Blue
        arr_display[:, :, 2] = arr_data[:, :, 1] # Red = Green
        arr_display[:, :, 1] = arr_data[:, :, 2] # Green = Red

    def translate_color(self, x, y, color_int):
        alpha = (color_int >> 24) & 0xFF
        red   = (color_int >> 16) & 0xFF
        green = (color_int >> 8)  & 0xFF
        blue  = color_int         & 0xFF
        # Swap Red/Green
        return (alpha << 24) | (green << 16) | (red << 8) | blue

    def apply_shader_to_rect(self, rect):
        left = max(0, int(rect.left()))
        top = max(0, int(rect.top()))
        right = min(self.data_image.width(), int(rect.right()))
        bottom = min(self.data_image.height(), int(rect.bottom()))

        for x in range(left, right):
            for y in range(top, bottom):
                src_pixel = self.data_image.pixel(x, y)
                display_pixel = self.translate_color(x, y, src_pixel)
                self.display_image.setPixel(x, y, display_pixel)

    # --- IMAGE LOADING ---

    def load_image(self, path):
        if not os.path.exists(path):
            print(f"Error: {path}")
            return

        img = QImage(path)
        if img.isNull(): return
        
        self.data_image = img.convertToFormat(QImage.Format_ARGB32)
        self.display_image = QImage(self.data_image.size(), QImage.Format_ARGB32)

        self.apply_shader_numpy()

        pixmap = QPixmap.fromImage(self.display_image)
        self._scene.clear()
        self.image_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self.image_item)
        self.setSceneRect(self.image_item.boundingRect())

    # --- INPUT ROUTING ---

    def get_interaction_data(self, window_pos):
        """Helper to get (x, y, color) safely"""
        if not self.image_item: return None, None, None
        
        scene_pos = self.mapToScene(window_pos.toPoint())
        item_pos = self.image_item.mapFromScene(scene_pos)
        x, y = int(item_pos.x()), int(item_pos.y())
        
        if 0 <= x < self.data_image.width() and 0 <= y < self.data_image.height():
            # Get color from the SOURCE (Data) image
            col = self.data_image.pixelColor(x, y)
            return x, y, col
        return x, y, QColor(0,0,0) # Out of bounds

    def mousePressEvent(self, event: QMouseEvent):
        # 1. GLOBAL PANNING (Middle Mouse)
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._last_pan_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return

        # 2. MODE HANDLING
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
        # 1. PANNING
        if self._is_panning:
            delta = event.position() - self._last_pan_pos
            self._last_pan_pos = event.position()
            hs = self.horizontalScrollBar()
            vs = self.verticalScrollBar()
            hs.setValue(hs.value() - delta.x())
            vs.setValue(vs.value() - delta.y())
            event.accept()
            return
        
        # 2. MODE HANDLING (DRAG)
        x, y, col = self.get_interaction_data(event.position())
        
        if event.buttons() & Qt.LeftButton:
            self.current_mode.on_left_drag(self, x, y, col)
        elif event.buttons() & Qt.RightButton:
            self.current_mode.on_right_drag(self, x, y, col)
            
        # Standard hover processing
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
        self.setWindowTitle("Pixel Editor - Modes")
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
        toolbar.addWidget(QLabel("Mode: "))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Drawing Mode", PaintMode())
        self.mode_combo.addItem("Debug Mode", DebugMode())
        
        # Connect signal
        self.mode_combo.currentIndexChanged.connect(self.change_mode)
        toolbar.addWidget(self.mode_combo)
        
        toolbar.addSeparator()

        # --- COLOR DISPLAY ---
        toolbar.addWidget(QLabel(" Color: "))
        self.color_display = QLabel()
        self.color_display.setFixedSize(24, 24)
        self.color_display.setStyleSheet("border: 1px solid #555;") 
        toolbar.addWidget(self.color_display)
        
        toolbar.addSeparator()

        # --- BRUSH SIZE ---
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

    def change_mode(self, index):
        # Retrieve the class instance stored in the UserData of the ComboBox
        new_mode = self.mode_combo.currentData()
        self.viewer.current_mode = new_mode
        print(f"Switched to: {new_mode.getName()}")

    def update_color_display(self, color):
        pixmap = QPixmap(24, 24)
        pixmap.fill(color)
        self.color_display.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())