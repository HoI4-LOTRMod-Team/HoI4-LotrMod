import sys
import os
import numpy as np
from PIL import Image
import pytoshop
from pytoshop.user import nested_layers
from pytoshop.enums import ColorMode, Compression

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QScrollArea, QGroupBox, QGridLayout,
                               QToolButton, QGraphicsView, QGraphicsScene, QPushButton,
                               QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
                               QAbstractItemView, QGraphicsPixmapItem, QGraphicsItem)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPen
from PySide6.QtCore import Qt, QSize

# --- CONFIGURATION ---
HARDCODED_PATH = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\retrievals\new-tool-test'
THUMBNAIL_SIZE = QSize(80, 80)

class DraggableLayerItem(QGraphicsPixmapItem):
    """Custom item that allows selection, dragging, and draws a dashed border when selected."""
    def __init__(self, pixmap, img_path):
        super().__init__(pixmap)
        self.img_path = img_path
        # Enable selection and moving
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        # Draw a bounding box if the item is currently selected
        if self.isSelected():
            pen = QPen(Qt.white, 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

class SimplePhotoshop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Element Compositor")
        self.resize(1200, 700)

        # State tracking
        self.active_layers = {}      # {filepath: DraggableLayerItem}
        self.thumbnail_buttons = {}  # {filepath: QToolButton}

        self.setup_ui()
        self.load_elements()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- LEFT PANEL: Categories and Thumbnails ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.scroll_content)

        export_btn = QPushButton("Export to PSD")
        export_btn.setMinimumHeight(40)
        export_btn.setStyleSheet("font-weight: bold; background-color: #2d89ef; color: white;")
        export_btn.clicked.connect(self.export_psd)

        left_layout.addWidget(scroll_area)
        left_layout.addWidget(export_btn)
        
        # --- MIDDLE PANEL: Canvas / Document View ---
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setBackgroundBrush(Qt.darkGray)

        # --- RIGHT PANEL: Layers Panel ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.layer_list = QListWidget()
        self.layer_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.layer_list.model().rowsMoved.connect(self.sync_z_values)
        
        right_layout.addWidget(self.layer_list)

        # Add to main layout (Left: 1, Canvas: 3, Right: 1)
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.view, 3)
        main_layout.addWidget(right_panel, 1)

    def load_elements(self):
        if not os.path.exists(HARDCODED_PATH):
            QMessageBox.warning(self, "Error", f"Path not found: {HARDCODED_PATH}")
            return

        folders = [f for f in os.listdir(HARDCODED_PATH) if os.path.isdir(os.path.join(HARDCODED_PATH, f))]
        
        # We assign an initial Z-index based on category folder order
        for z_index, folder in enumerate(sorted(folders)):
            folder_path = os.path.join(HARDCODED_PATH, folder)
            group_box = QGroupBox(folder)
            grid_layout = QGridLayout(group_box)
            images = [img for img in os.listdir(folder_path) if img.lower().endswith('.png')]
            
            row, col = 0, 0
            for img_name in images:
                img_path = os.path.join(folder_path, img_name)
                
                btn = QToolButton()
                btn.setCheckable(True)
                btn.setIcon(QIcon(img_path))
                btn.setIconSize(THUMBNAIL_SIZE)
                btn.setToolTip(img_name)
                
                # Save button reference so we can uncheck it later if deleted via keyboard
                self.thumbnail_buttons[img_path] = btn
                btn.toggled.connect(lambda checked, p=img_path, z=z_index: self.toggle_layer(checked, p, z))
                
                grid_layout.addWidget(btn, row, col)
                col += 1
                if col >= 3:
                    col = 0; row += 1
                    
            self.scroll_layout.addWidget(group_box)

    def toggle_layer(self, checked, img_path, default_z_index):
        if checked:
            # 1. Add to Canvas
            item = DraggableLayerItem(QPixmap(img_path), img_path)
            self.scene.addItem(item)
            self.active_layers[img_path] = item
            
            # 2. Add to Layers Panel (Top of the list = Front of canvas)
            list_item = QListWidgetItem(os.path.basename(img_path))
            list_item.setData(Qt.UserRole, img_path) # Store path secretly in the item
            self.layer_list.insertItem(0, list_item) 
            
            self.sync_z_values() # Ensure correct drawing order
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
        else:
            # 1. Remove from Canvas
            if img_path in self.active_layers:
                item = self.active_layers.pop(img_path)
                self.scene.removeItem(item)
            
            # 2. Remove from Layers Panel
            for i in range(self.layer_list.count()):
                list_item = self.layer_list.item(i)
                if list_item.data(Qt.UserRole) == img_path:
                    self.layer_list.takeItem(i)
                    break

    def sync_z_values(self, *args):
        """Reads the QListWidget from bottom to top and assigns Z-values accordingly."""
        count = self.layer_list.count()
        for i in range(count):
            list_item = self.layer_list.item(i)
            img_path = list_item.data(Qt.UserRole)
            if img_path in self.active_layers:
                # Top of the list (index 0) gets highest Z-value
                self.active_layers[img_path].setZValue(count - i)

    def keyPressEvent(self, event):
        """Listen for Delete/Backspace keys to remove selected canvas elements."""
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            for item in self.scene.selectedItems():
                if isinstance(item, DraggableLayerItem):
                    # Unchecking the button triggers toggle_layer(False), handling all cleanup!
                    self.thumbnail_buttons[item.img_path].setChecked(False)
        super().keyPressEvent(event)

    def export_psd(self):
        if not self.active_layers:
            QMessageBox.information(self, "Export", "No layers selected.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save PSD", "", "Photoshop Document (*.psd)")
        if not save_path: return

        try:
            psd_layers = []
            
            # Sort by Z-value descending (Highest Z-value goes into PSD first)
            sorted_items = sorted(self.active_layers.values(), key=lambda item: item.zValue(), reverse=True)

            for item in sorted_items:
                filepath = item.img_path
                img = Image.open(filepath).convert("RGBA")
                r, g, b, a = img.split()
                channels = {-1: np.array(a), 0: np.array(r), 1: np.array(g), 2: np.array(b)}
                
                # Fetch new X/Y position from the canvas item!
                pos = item.pos()
                top_offset = int(pos.y())
                left_offset = int(pos.x())
                
                layer = nested_layers.Image(
                    name=os.path.basename(filepath),
                    visible=True,
                    top=top_offset,
                    left=left_offset,
                    bottom=top_offset + img.height,
                    right=left_offset + img.width,
                    channels=channels
                )
                psd_layers.append(layer)

            psd_document = nested_layers.nested_layers_to_psd(
                psd_layers, color_mode=ColorMode.rgb, compression=Compression.raw
            )
            with open(save_path, 'wb') as fd:
                psd_document.write(fd)

            QMessageBox.information(self, "Success", "PSD successfully exported!")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SimplePhotoshop()
    window.show()
    sys.exit(app.exec())