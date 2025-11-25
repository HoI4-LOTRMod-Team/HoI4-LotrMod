import sys
import os
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QMainWindow, QToolBar, 
                               QLabel, QWidget, QSizePolicy)
from PySide6.QtGui import (QPixmap, QPainter, QImage, QColor, QMouseEvent, 
                           QAction, QActionGroup)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal

# --- CONFIGURATION ---
HARDCODED_IMAGE_PATH = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\map\provinces - Copy.bmp'
# ---------------------

class EditorView(QGraphicsView):
    # Signal to notify the Main Window when the active color changes
    colorChanged = Signal(QColor)

    def __init__(self):
        super().__init__()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # Helper variables
        self.image_item = None
        self.qimage = None
        self.current_color = QColor(255, 0, 0) # Default Red
        self.brush_size = 1

        # State flags
        self._is_panning = False
        self._is_painting = False
        self._last_pan_pos = QPointF()

        # UI Setup
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def set_brush_size(self, size):
        self.brush_size = size
        
    def emit_current_color(self):
        # Helper to update UI on startup
        self.colorChanged.emit(self.current_color)

    def load_image(self, path):
        if not os.path.exists(path):
            print(f"Error: Image not found at {path}")
            return

        self.qimage = QImage(path)
        if self.qimage.isNull():
            print("Error: Failed to load image data.")
            return
        
        self.qimage = self.qimage.convertToFormat(QImage.Format_ARGB32)

        pixmap = QPixmap.fromImage(self.qimage)
        self._scene.clear()
        self.image_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self.image_item)
        self.setSceneRect(self.image_item.boundingRect())

    # --- INPUT HANDLING ---

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

    # --- LOGIC ---

    def _get_image_coords(self, window_pos):
        if not self.image_item:
            return None, None
        
        scene_pos = self.mapToScene(window_pos.toPoint())
        item_pos = self.image_item.mapFromScene(scene_pos)
        x = int(item_pos.x())
        y = int(item_pos.y())
        return x, y

    def pick_color(self, window_pos):
        x, y = self._get_image_coords(window_pos)
        if 0 <= x < self.qimage.width() and 0 <= y < self.qimage.height():
            self.current_color = self.qimage.pixelColor(x, y)
            # Emit signal to update Toolbar
            self.colorChanged.emit(self.current_color)

    def paint_at_cursor(self, window_pos):
        x, y = self._get_image_coords(window_pos)
        
        painter = QPainter(self.qimage)
        painter.setBrush(self.current_color)
        painter.setPen(Qt.NoPen)
        # Turn off AA for pixel-perfect edges
        painter.setRenderHint(QPainter.Antialiasing, False) 

        # FIX 1: Handle Size 1 vs Larger Sizes
        if self.brush_size == 1:
            # drawPoint is much more reliable for single pixels than drawEllipse
            painter.setPen(self.current_color) 
            painter.drawPoint(x, y)
        else:
            # FIX 2: Use QRectF (Floats) to prevent int-rounding distortion
            radius = self.brush_size / 2.0
            rect = QRectF(x - radius, y - radius, float(self.brush_size), float(self.brush_size))
            painter.drawEllipse(rect)
        
        painter.end()
        self.image_item.setPixmap(QPixmap.fromImage(self.qimage))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Editor")
        self.resize(900, 600)

        self.viewer = EditorView()
        self.setCentralWidget(self.viewer)
        
        # Connect the view's signal to our update slot
        self.viewer.colorChanged.connect(self.update_color_display)

        self.setup_toolbar()
        
        # Load Image
        self.viewer.load_image(HARDCODED_IMAGE_PATH)
        
        # Initialize the color display with default color
        self.viewer.emit_current_color()

    def setup_toolbar(self):
        toolbar = QToolBar("Brushes")
        toolbar.setIconSize(toolbar.iconSize() * 1.5) # Make things a bit bigger
        self.addToolBar(toolbar)

        # 1. Color Display Label
        lbl_intro = QLabel("Active Color: ")
        toolbar.addWidget(lbl_intro)

        self.color_display = QLabel()
        self.color_display.setFixedSize(24, 24)
        # Add a small border so white colors are visible
        self.color_display.setStyleSheet("border: 1px solid #555;") 
        toolbar.addWidget(self.color_display)
        
        # Spacer
        spacer = QWidget()
        spacer.setFixedWidth(20)
        toolbar.addWidget(spacer)

        # 2. Brush Sizes
        toolbar.addWidget(QLabel("Size: "))
        brush_group = QActionGroup(self)
        
        sizes = [
            ("1px", 1),
            ("3px", 3),
            ("5px", 5),
            ("10px", 10),
            ("20px", 20)
        ]

        for label, size in sizes:
            action = QAction(label, self)
            action.setCheckable(True)
            if size == 1:
                action.setChecked(True)
            
            action.triggered.connect(lambda checked, s=size: self.viewer.set_brush_size(s))
            brush_group.addAction(action)
            toolbar.addAction(action)

    def update_color_display(self, color):
        """
        Create a small pixmap of the new color and set it to the label
        """
        pixmap = QPixmap(24, 24)
        pixmap.fill(color)
        self.color_display.setPixmap(pixmap)
        
        # Optional: Print to console for debugging
        print(f"UI Color Updated: {color.name()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())