import sys
import os
import numpy as np
from PIL import Image
import pytoshop
from pytoshop.user import nested_layers
from pytoshop.enums import ColorMode, Compression

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QScrollArea, QGridLayout,
                               QToolButton, QGraphicsView, QGraphicsScene, QPushButton,
                               QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
                               QAbstractItemView, QGraphicsPixmapItem, QGraphicsItem,
                               QSlider, QLabel, QFormLayout, QSpinBox, QGraphicsRectItem,
                               QGroupBox)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPen, QBrush, QImage
from PySide6.QtCore import Qt, QSize

# --- CONFIGURATION ---
HARDCODED_PATH = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\retrievals\new-tool-test'
THUMBNAIL_SIZE = QSize(80, 80)

class DraggableLayerItem(QGraphicsPixmapItem):
    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path
        self.pil_img = Image.open(img_path).convert("RGBA")
        
        # We track our own scale and rotation now, instead of using Qt's hardware transforms
        self.current_scale = 1.0
        self.current_rot = 0.0
        self.transformed_pil_img = self.pil_img
        self._img_data = None # Holds raw bytes in memory so QImage doesn't crash
        
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

    def update_transform(self, scale, rot):
        """Uses Pillow to mathematically resample the image live."""
        # Save old center in scene coordinates to prevent the item from jumping when resized
        old_scene_center = self.scenePos() + self.boundingRect().center() if self.scene() else None
        
        self.current_scale = scale
        self.current_rot = rot
        
        img = self.pil_img.copy()
        
        if scale != 1.0:
            new_w = max(1, int(img.width * scale))
            new_h = max(1, int(img.height * scale))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        if rot != 0.0:
            img = img.rotate(-rot, expand=True, resample=Image.Resampling.BICUBIC)
        
        self.transformed_pil_img = img
        
        # Convert raw Pillow bytes into a QPixmap
        self._img_data = img.tobytes("raw", "RGBA")
        qimg = QImage(self._img_data, img.width, img.height, QImage.Format_RGBA8888)
        self.setPixmap(QPixmap.fromImage(qimg))
        
        # Shift position so the visual center remains exactly where it was
        if old_scene_center:
            new_center_local = self.boundingRect().center()
            self.setPos(old_scene_center.x() - new_center_local.x(), old_scene_center.y() - new_center_local.y())

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(Qt.white, 1, Qt.DashLine)
            pen.setCosmetic(True) # Ensures the dashed line stays 1px thick even when zoomed in 1000%
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

class ZoomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        # We purposely REMOVED the SmoothPixmapTransform here! 
        # Now, when you zoom in, Qt uses 'Nearest Neighbor' to show you the raw, chunky pixels.
        self.setBackgroundBrush(Qt.darkGray)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag) 

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            zoom_in_factor = 1.15
            zoom_out_factor = 1.0 / zoom_in_factor
            if event.angleDelta().y() > 0:
                self.scale(zoom_in_factor, zoom_in_factor)
            else:
                self.scale(zoom_out_factor, zoom_out_factor)
        else:
            super().wheelEvent(event)

class SimplePhotoshop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Element Compositor")
        self.resize(1200, 750)

        self.active_layers = {}      
        self.thumbnail_buttons = {}  
        self._updating_ui = False 
        
        self.canvas_w = 110
        self.canvas_h = 100

        self.setup_ui()
        self.load_elements()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

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
        
        right_side_container = QWidget()
        right_side_layout = QVBoxLayout(right_side_container)
        right_side_layout.setContentsMargins(0, 0, 0, 0)

        workspace_widget = QWidget()
        workspace_layout = QHBoxLayout(workspace_widget)
        workspace_layout.setContentsMargins(0, 0, 0, 0)

        self.scene = QGraphicsScene()
        self.scene.selectionChanged.connect(self.on_selection_changed)
        
        self.canvas_rect_item = QGraphicsRectItem(0, 0, self.canvas_w, self.canvas_h)
        self.canvas_rect_item.setBrush(QBrush(Qt.white))
        self.canvas_rect_item.setPen(QPen(Qt.black, 1, Qt.DashLine))
        self.canvas_rect_item.setZValue(-1000) 
        self.scene.addItem(self.canvas_rect_item)
        
        self.view = ZoomGraphicsView(self.scene)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        canvas_group = QGroupBox("Document Canvas")
        canvas_layout = QHBoxLayout(canvas_group)
        self.spin_w = QSpinBox()
        self.spin_w.setRange(10, 5000)
        self.spin_w.setValue(self.canvas_w)
        self.spin_h = QSpinBox()
        self.spin_h.setRange(10, 5000)
        self.spin_h.setValue(self.canvas_h)
        
        apply_canvas_btn = QPushButton("Apply")
        apply_canvas_btn.clicked.connect(self.update_canvas_size)
        
        canvas_layout.addWidget(QLabel("W:"))
        canvas_layout.addWidget(self.spin_w)
        canvas_layout.addWidget(QLabel("H:"))
        canvas_layout.addWidget(self.spin_h)
        canvas_layout.addWidget(apply_canvas_btn)
        
        self.layer_list = QListWidget()
        self.layer_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.layer_list.model().rowsMoved.connect(self.sync_z_values)

        right_layout.addWidget(canvas_group, 0)
        right_layout.addWidget(self.layer_list, 1)

        workspace_layout.addWidget(self.view, 3)
        workspace_layout.addWidget(right_panel, 1)

        props_group = QGroupBox("Transform Properties")
        props_layout = QFormLayout(props_group)
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(1, 200) 
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.apply_transform)
        
        self.rot_slider = QSlider(Qt.Horizontal)
        self.rot_slider.setRange(-180, 180)
        self.rot_slider.setValue(0)
        self.rot_slider.valueChanged.connect(self.apply_transform)
        
        self.scale_label = QLabel("100%")
        self.rot_label = QLabel("0°")

        props_layout.addRow("Scale:", self.scale_slider)
        props_layout.addRow("", self.scale_label)
        props_layout.addRow("Rotate:", self.rot_slider)
        props_layout.addRow("", self.rot_label)
        
        self.enable_properties(False)

        right_side_layout.addWidget(workspace_widget, 1)
        right_side_layout.addWidget(props_group, 0)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_side_container, 4)
        
        self.update_canvas_size()

    def update_canvas_size(self):
        self.canvas_w = self.spin_w.value()
        self.canvas_h = self.spin_h.value()
        self.canvas_rect_item.setRect(0, 0, self.canvas_w, self.canvas_h)
        buffer = max(self.canvas_w, self.canvas_h)
        self.scene.setSceneRect(-buffer, -buffer, self.canvas_w + (buffer*2), self.canvas_h + (buffer*2))
        self.view.centerOn(self.canvas_rect_item)

    def load_elements(self):
        if not os.path.exists(HARDCODED_PATH):
            QMessageBox.warning(self, "Error", f"Path not found: {HARDCODED_PATH}")
            return

        folders = [f for f in os.listdir(HARDCODED_PATH) if os.path.isdir(os.path.join(HARDCODED_PATH, f))]
        
        for z_index, folder in enumerate(sorted(folders)):
            folder_path = os.path.join(HARDCODED_PATH, folder)
            
            category_widget = QWidget()
            category_layout = QVBoxLayout(category_widget)
            category_layout.setContentsMargins(0, 0, 0, 0)
            
            toggle_btn = QPushButton(f"v {folder}")
            toggle_btn.setStyleSheet("text-align: left; font-weight: bold; padding: 5px; background-color: #ddd;")
            
            content_widget = QWidget()
            grid_layout = QGridLayout(content_widget)
            
            toggle_btn.clicked.connect(lambda checked=False, cw=content_widget, btn=toggle_btn, name=folder: self.toggle_category(cw, btn, name))
            
            images = [img for img in os.listdir(folder_path) if img.lower().endswith('.png')]
            
            row, col = 0, 0
            for img_name in images:
                img_path = os.path.join(folder_path, img_name)
                btn = QToolButton()
                btn.setCheckable(True)
                btn.setIcon(QIcon(img_path))
                btn.setIconSize(THUMBNAIL_SIZE)
                btn.setToolTip(img_name)
                
                self.thumbnail_buttons[img_path] = btn
                btn.toggled.connect(lambda checked, p=img_path, z=z_index: self.toggle_layer(checked, p, z))
                
                grid_layout.addWidget(btn, row, col)
                col += 1
                if col >= 3:
                    col = 0; row += 1
                    
            category_layout.addWidget(toggle_btn)
            category_layout.addWidget(content_widget)
            self.scroll_layout.addWidget(category_widget)

    def toggle_category(self, content_widget, btn, folder_name):
        is_visible = content_widget.isVisible()
        content_widget.setVisible(not is_visible)
        btn.setText(f"v {folder_name}" if not is_visible else f"> {folder_name}")

    def toggle_layer(self, checked, img_path, default_z_index):
        if checked:
            item = DraggableLayerItem(img_path)
            
            # Auto-Fit logic mapped to our new Pillow update function
            img_w = item.pil_img.width
            img_h = item.pil_img.height
            scale = min(self.canvas_w / img_w, self.canvas_h / img_h)
            
            # Initial generation of the downsampled image
            item.update_transform(scale, 0.0) 
            
            # Center it on the canvas
            center = item.boundingRect().center()
            target_x = (self.canvas_w / 2) - center.x()
            target_y = (self.canvas_h / 2) - center.y()
            item.setPos(target_x, target_y)
            
            self.scene.addItem(item)
            self.active_layers[img_path] = item
            
            list_item = QListWidgetItem(os.path.basename(img_path))
            list_item.setData(Qt.UserRole, img_path)
            self.layer_list.insertItem(0, list_item) 
            
            self.sync_z_values()
            self.scene.clearSelection()
            item.setSelected(True)
        else:
            if img_path in self.active_layers:
                item = self.active_layers.pop(img_path)
                self.scene.removeItem(item)
            
            for i in range(self.layer_list.count()):
                list_item = self.layer_list.item(i)
                if list_item.data(Qt.UserRole) == img_path:
                    self.layer_list.takeItem(i)
                    break

    def sync_z_values(self, *args):
        count = self.layer_list.count()
        for i in range(count):
            list_item = self.layer_list.item(i)
            img_path = list_item.data(Qt.UserRole)
            if img_path in self.active_layers:
                self.active_layers[img_path].setZValue(count - i)

    def on_selection_changed(self):
        selected_items = self.scene.selectedItems()
        if len(selected_items) == 1 and isinstance(selected_items[0], DraggableLayerItem):
            self._updating_ui = True
            item = selected_items[0]
            
            # Read our custom stored variables instead of Qt's hardware variables
            current_scale = int(item.current_scale * 100)
            current_rot = int(item.current_rot)
            
            current_scale = max(self.scale_slider.minimum(), min(current_scale, self.scale_slider.maximum()))
            
            self.scale_slider.setValue(current_scale)
            self.rot_slider.setValue(current_rot)
            self.scale_label.setText(f"{current_scale}%")
            self.rot_label.setText(f"{current_rot}°")
            
            self.enable_properties(True)
            self._updating_ui = False
        else:
            self.enable_properties(False)

    def apply_transform(self):
        if self._updating_ui: return
        selected_items = self.scene.selectedItems()
        if not selected_items: return
        item = selected_items[0]
        
        scale_val = self.scale_slider.value()
        rot_val = self.rot_slider.value()
        
        # Trigger the live Pillow generation
        item.update_transform(scale_val / 100.0, rot_val)
        
        self.scale_label.setText(f"{scale_val}%")
        self.rot_label.setText(f"{rot_val}°")

    def enable_properties(self, enable):
        self.scale_slider.setEnabled(enable)
        self.rot_slider.setEnabled(enable)
        if not enable:
            self.scale_label.setText("-")
            self.rot_label.setText("-")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            for item in self.scene.selectedItems():
                if isinstance(item, DraggableLayerItem):
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
            sorted_items = sorted(self.active_layers.values(), key=lambda item: item.zValue(), reverse=True)

            for item in sorted_items:
                filepath = item.img_path
                
                # --- MASSIVE EXPORT SIMPLIFICATION ---
                # We no longer need to resize or rotate! The item already holds the perfectly processed Image.
                img = item.transformed_pil_img 
                
                # Because the bounding box matches exactly, the item's raw position IS the offset.
                left_offset = int(item.scenePos().x())
                top_offset = int(item.scenePos().y())
                # -------------------------------------
                
                r, g, b, a = img.split()
                channels = {-1: np.array(a), 0: np.array(r), 1: np.array(g), 2: np.array(b)}
                
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
                psd_layers, 
                color_mode=ColorMode.rgb, 
                compression=Compression.raw,
                size=(self.canvas_h, self.canvas_w) 
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