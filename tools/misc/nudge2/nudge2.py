import sys
import os
import numpy as np # <--- NEW DEPENDENCY
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QMainWindow, QToolBar, 
                               QLabel, QWidget)
from PySide6.QtGui import (QPixmap, QPainter, QImage, QColor, QMouseEvent, 
                           QAction, QActionGroup)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal

HARDCODED_IMAGE_PATH = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\provinces - Copy.bmp'

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

        self._is_panning = False
        self._is_painting = False
        self._last_pan_pos = QPointF()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing, False)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def set_brush_size(self, size):
        self.brush_size = size

    def emit_current_color(self):
        self.colorChanged.emit(self.current_color)

    # ============================================================
    #  NUMPY SHADER (For the Full Image)
    # ============================================================
    def apply_shader_numpy(self):
        """
        Uses NumPy to process the entire image instantly.
        """
        width = self.data_image.width()
        height = self.data_image.height()

        # 1. Access raw memory of the Data Image
        ptr_data = self.data_image.constBits()
        # DELETED: ptr_data.setsize(...) <-- Not needed in PySide6
        
        # Create a NumPy view (no copy, just a wrapper around existing memory)
        # Note: We use extended slicing to ensure we don't hit size mismatch errors 
        # if the image has memory padding (bytesPerLine > width * 4).
        arr_data = np.frombuffer(ptr_data, np.uint8).reshape((height, -1))
        # Now we slice the actual pixel data (ignoring potential padding at the end of rows)
        # We reshape to (Height, Width, 4)
        arr_data = arr_data[:, :width * 4].reshape((height, width, 4))

        # 2. Access raw memory of Display Image (Target)
        ptr_display = self.display_image.bits()
        # DELETED: ptr_display.setsize(...) <-- Not needed in PySide6
        
        arr_display = np.frombuffer(ptr_display, np.uint8).reshape((height, -1))
        arr_display = arr_display[:, :width * 4].reshape((height, width, 4))

        # 3. APPLY SHADER LOGIC (Vectorized)
        # B=0, G=1, R=2, A=3
        
        # Copy Alpha and Blue unchanged
        arr_display[:, :, 3] = arr_data[:, :, 3] # Alpha
        arr_display[:, :, 0] = arr_data[:, :, 0] # Blue

        # SWAP RED (2) AND GREEN (1)
        arr_display[:, :, 2] = arr_data[:, :, 1] # Target Red gets Source Green
        arr_display[:, :, 1] = arr_data[:, :, 2] # Target Green gets Source Red


    # ============================================================
    #  PYTHON SHADER (For Small Updates/Painting)
    # ============================================================
    def translate_color(self, x, y, color_int):
        """Keeping the Python loop for small updates (brush strokes)"""
        alpha = (color_int >> 24) & 0xFF
        red   = (color_int >> 16) & 0xFF
        green = (color_int >> 8)  & 0xFF
        blue  = color_int         & 0xFF

        # The Logic: Swap Red and Green
        new_red = green
        new_green = red
        new_blue = blue
        
        return (alpha << 24) | (new_red << 16) | (new_green << 8) | new_blue

    def apply_shader_to_rect(self, rect):
        left = max(0, int(rect.left()))
        top = max(0, int(rect.top()))
        right = min(self.data_image.width(), int(rect.right()))
        bottom = min(self.data_image.height(), int(rect.bottom()))

        # For very large brushes (e.g. > 50px), you could switch to NumPy here too,
        # but for small edits, the pure Python loop is actually faster than 
        # the overhead of creating NumPy arrays.
        for x in range(left, right):
            for y in range(top, bottom):
                src_pixel = self.data_image.pixel(x, y)
                display_pixel = self.translate_color(x, y, src_pixel)
                self.display_image.setPixel(x, y, display_pixel)

    # ============================================================

    def load_image(self, path):
        if not os.path.exists(path):
            print(f"Error: Image not found at {path}")
            return

        img = QImage(path)
        if img.isNull(): return
        
        self.data_image = img.convertToFormat(QImage.Format_ARGB32)
        self.display_image = QImage(self.data_image.size(), QImage.Format_ARGB32)

        # USE NUMPY FOR INITIAL LOAD
        print("Processing initial shader pass (NumPy)...")
        self.apply_shader_numpy() # <--- Fast!

        pixmap = QPixmap.fromImage(self.display_image)
        self._scene.clear()
        self.image_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self.image_item)
        self.setSceneRect(self.image_item.boundingRect())

    # ... [Rest of Input Handling and Paint logic remains exactly the same] ...
    def _get_image_coords(self, window_pos):
        if not self.image_item: return None, None
        scene_pos = self.mapToScene(window_pos.toPoint())
        item_pos = self.image_item.mapFromScene(scene_pos)
        return int(item_pos.x()), int(item_pos.y())

    def pick_color(self, window_pos):
        x, y = self._get_image_coords(window_pos)
        if 0 <= x < self.data_image.width() and 0 <= y < self.data_image.height():
            self.current_color = self.data_image.pixelColor(x, y)
            self.colorChanged.emit(self.current_color)

    def paint_at_cursor(self, window_pos):
        x, y = self._get_image_coords(window_pos)
        
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

        safe_rect = dirty_rect.adjusted(-1, -1, 1, 1)
        self.apply_shader_to_rect(safe_rect)
        self.image_item.setPixmap(QPixmap.fromImage(self.display_image))
    
    # ... [Mouse Events same as previous code] ...
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton or event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._last_pan_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.AltModifier:
                self.pick_color(event.position())
            else:
                self._is_painting = True
                self.paint_at_cursor(event.position())
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
        elif self._is_painting:
            self.paint_at_cursor(event.position())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._is_painting = False
        elif event.button() == Qt.RightButton or event.button() == Qt.MiddleButton:
            self._is_panning = False
            self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event):
        zoom_in = 1.25
        zoom_out = 1 / zoom_in
        factor = zoom_in if event.angleDelta().y() > 0 else zoom_out
        self.scale(factor, factor)

# ... [MainWindow remains exactly the same] ...
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Editor - (NumPy Shader)")
        self.resize(900, 600)

        self.viewer = EditorView()
        self.setCentralWidget(self.viewer)
        self.viewer.colorChanged.connect(self.update_color_display)
        self.setup_toolbar()
        
        self.viewer.load_image(HARDCODED_IMAGE_PATH)
        self.viewer.emit_current_color()

    def setup_toolbar(self):
        toolbar = QToolBar("Brushes")
        self.addToolBar(toolbar)

        toolbar.addWidget(QLabel("Data Color: "))
        self.color_display = QLabel()
        self.color_display.setFixedSize(24, 24)
        self.color_display.setStyleSheet("border: 1px solid #555;") 
        toolbar.addWidget(self.color_display)
        
        widget = QWidget()
        widget.setFixedWidth(20)
        toolbar.addWidget(widget)

        toolbar.addWidget(QLabel("Brush Size: "))
        brush_group = QActionGroup(self)
        sizes = [("1px", 1), ("3px", 3), ("5px", 5), ("10px", 10), ("20px", 20)]

        for label, size in sizes:
            action = QAction(label, self)
            action.setCheckable(True)
            if size == 10:
                action.setChecked(True)
                self.viewer.set_brush_size(size)
            action.triggered.connect(lambda checked, s=size: self.viewer.set_brush_size(s))
            brush_group.addAction(action)
            toolbar.addAction(action)

    def update_color_display(self, color):
        pixmap = QPixmap(24, 24)
        pixmap.fill(color)
        self.color_display.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())