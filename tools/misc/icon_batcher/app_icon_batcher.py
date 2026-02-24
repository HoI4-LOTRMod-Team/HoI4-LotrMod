import sys
import os
import numpy as np
from PIL import Image
import pytoshop
from pytoshop.user import nested_layers
from pytoshop.enums import ColorMode, Compression

from psd_tools import PSDImage

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                               QVBoxLayout, QScrollArea, QGridLayout,
                               QToolButton, QGraphicsView, QGraphicsScene, QPushButton,
                               QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
                               QAbstractItemView, QGraphicsPixmapItem, QGraphicsItem,
                               QSlider, QLabel, QFormLayout, QSpinBox, QGraphicsRectItem,
                               QGroupBox, QSplitter, QStackedWidget)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPen, QBrush, QImage
from PySide6.QtCore import Qt, QSize

# --- CONFIGURATION ---
HARDCODED_PATH = r'C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\focuses_and_ideas'
THUMBNAIL_SIZE = QSize(80, 80)

class DraggableLayerItem(QGraphicsPixmapItem):
    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path
        self.pil_img = Image.open(img_path).convert("RGBA")
        
        self.current_scale = 1.0
        self.current_rot = 0.0
        self.transformed_pil_img = self.pil_img
        self._img_data = None 
        
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

    def update_transform(self, scale, rot):
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
        
        self._img_data = img.tobytes("raw", "RGBA")
        qimg = QImage(self._img_data, img.width, img.height, QImage.Format_RGBA8888)
        self.setPixmap(QPixmap.fromImage(qimg))
        
        if old_scene_center:
            new_center_local = self.boundingRect().center()
            self.setPos(old_scene_center.x() - new_center_local.x(), old_scene_center.y() - new_center_local.y())

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(Qt.white, 1, Qt.DashLine)
            pen.setCosmetic(True) 
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

class ZoomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
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
        self.resize(2100, 1150)

        self.active_layers = {}      
        self.thumbnail_buttons = {}  
        self._updating_ui = False 

        self.current_template_path = None
        self.template_bg_item = None
        
        self.canvas_w = 110
        self.canvas_h = 100

        self.setup_ui()
        self.load_elements()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # 1. Use QSplitter to allow the user to resize panels
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # --- LEFT PANEL (Assets) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Top Section: Grid for Folder Buttons
        self.folder_btn_container = QWidget()
        self.folder_btn_layout = QGridLayout(self.folder_btn_container)
        self.folder_btn_layout.setAlignment(Qt.AlignTop)

        # Middle Section: Stacked widget to switch between icon grids
        self.icon_stacked_widget = QStackedWidget()
        self.empty_page = QWidget() # Page 0: Represents "All Folders Collapsed"
        self.icon_stacked_widget.addWidget(self.empty_page)

        export_btn = QPushButton("Export to PSD")
        export_btn.setMinimumHeight(40)
        export_btn.setStyleSheet("font-weight: bold; background-color: #2d89ef; color: white;")
        export_btn.clicked.connect(self.export_psd)

        # Add the container directly instead of the scroll area
        left_layout.addWidget(self.folder_btn_container)
        left_layout.addWidget(self.icon_stacked_widget)
        left_layout.addWidget(export_btn)
        
        # --- RIGHT PANEL (Workspace) ---
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

        sidebar_panel = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_panel)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
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

        sidebar_layout.addWidget(canvas_group, 0)
        sidebar_layout.addWidget(self.layer_list, 1)

        workspace_layout.addWidget(self.view, 3)
        workspace_layout.addWidget(sidebar_panel, 1)

        props_group = QGroupBox("Transform Properties")
        props_layout = QFormLayout(props_group)
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(1, 150) 
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

        # Assemble Splitter and apply new default ratios
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(right_side_container)
        self.main_splitter.setSizes([450, 850])
        
        self.update_canvas_size()

    def update_canvas_size(self):
        self.canvas_w = self.spin_w.value()
        self.canvas_h = self.spin_h.value()
        self.canvas_rect_item.setRect(0, 0, self.canvas_w, self.canvas_h)
        buffer = max(self.canvas_w, self.canvas_h)
        self.scene.setSceneRect(-buffer, -buffer, self.canvas_w + (buffer*2), self.canvas_h + (buffer*2))
        self.view.centerOn(self.canvas_rect_item)

    def load_template(self, psd_path):
        from psd_tools import PSDImage
        
        for img_path, item in list(self.active_layers.items()):
            self.scene.removeItem(item)
            if img_path in self.thumbnail_buttons:
                self.thumbnail_buttons[img_path].setChecked(False)
        self.active_layers.clear()
        self.layer_list.clear()

        try:
            psd = PSDImage.open(psd_path)
            self.current_template_path = psd_path
            
            list_item = QListWidgetItem(f"[Base PSD] {os.path.basename(psd_path)}")
            list_item.setData(Qt.UserRole, "TEMPLATE_ITEM") 
            list_item.setBackground(QBrush(Qt.lightGray))
            self.layer_list.addItem(list_item)
            
            self.spin_w.setValue(psd.width)
            self.spin_h.setValue(psd.height)
            self.update_canvas_size()

            pil_preview = psd.composite()
            if pil_preview.mode != "RGBA":
                pil_preview = pil_preview.convert("RGBA")
                
            img_data = pil_preview.tobytes("raw", "RGBA")
            qimg = QImage(img_data, pil_preview.width, pil_preview.height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimg)

            if self.template_bg_item:
                self.scene.removeItem(self.template_bg_item)
                
            self.template_bg_item = QGraphicsPixmapItem(pixmap)
            self.template_bg_item.setPos(0, 0)
            self.scene.addItem(self.template_bg_item)
            
            self.sync_z_values()
            
        except Exception as e:
            QMessageBox.critical(self, "Template Error", f"Failed to load PSD template:\n{str(e)}")

    def load_elements(self):
        if not os.path.exists(HARDCODED_PATH):
            QMessageBox.warning(self, "Error", f"Path not found: {HARDCODED_PATH}")
            return

        folders = [f for f in os.listdir(HARDCODED_PATH) if os.path.isdir(os.path.join(HARDCODED_PATH, f))]
        
        self.folder_buttons = [] # Store reference to our top buttons for toggling

        # Track grid positions for the top folder buttons
        folder_row, folder_col = 0, 0
        max_folder_cols = 3 # You can change this to 4 or 5 if you want wider rows

        for z_index, folder in enumerate(sorted(folders)):
            folder_path = os.path.join(HARDCODED_PATH, folder)
            
            # --- 1. Create Top Folder Button ---
            folder_btn = QPushButton(folder)
            folder_btn.setCheckable(True)
            folder_btn.setStyleSheet("""
                QPushButton { font-weight: bold; padding: 8px 15px; background-color: #ddd; border-radius: 4px; }
                QPushButton:checked { background-color: #2d89ef; color: white; }
            """)
            
            # Add to the new grid layout
            self.folder_btn_layout.addWidget(folder_btn, folder_row, folder_col)
            self.folder_buttons.append(folder_btn)
            
            # Increment columns, wrap to next row if needed
            folder_col += 1
            if folder_col >= max_folder_cols:
                folder_col = 0
                folder_row += 1
            
            # --- 2. Create the Scrollable Grid for this Folder ---
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            content_widget = QWidget()
            grid_layout = QGridLayout(content_widget)
            grid_layout.setAlignment(Qt.AlignTop)
            scroll_area.setWidget(content_widget)
            
            # Add to Stacked Widget (Page Index will be z_index + 1)
            page_index = self.icon_stacked_widget.addWidget(scroll_area)
            
            # Connect the button click to our toggle logic
            folder_btn.clicked.connect(lambda checked, b=folder_btn, idx=page_index: self.on_folder_btn_clicked(checked, b, idx))
            
            # --- 3. Populate Grid ---
            images = [img for img in os.listdir(folder_path) if img.lower().endswith(('.png', '.psd'))]
            
            row, col = 0, 0
            for img_name in images:
                img_path = os.path.join(folder_path, img_name)
                tool_btn = QToolButton()
                is_template = img_name.lower().endswith('.psd')
                tool_btn.setCheckable(not is_template) 
                
                if is_template:
                    try:
                        from psd_tools import PSDImage
                        psd = PSDImage.open(img_path)
                        preview = psd.composite()
                        if preview.mode != "RGBA":
                            preview = preview.convert("RGBA")
                        
                        preview.thumbnail((THUMBNAIL_SIZE.width(), THUMBNAIL_SIZE.height()))
                        
                        img_data = preview.tobytes("raw", "RGBA")
                        qimg = QImage(img_data, preview.width, preview.height, QImage.Format_RGBA8888)
                        tool_btn.setIcon(QIcon(QPixmap.fromImage(qimg)))
                    except Exception as e:
                        print(f"Could not generate thumbnail for {img_name}: {e}")
                        tool_btn.setIcon(QIcon()) 
                        
                    tool_btn.clicked.connect(lambda checked, p=img_path: self.load_template(p))
                else:
                    tool_btn.setIcon(QIcon(img_path))
                    tool_btn.toggled.connect(lambda checked, p=img_path, z=z_index: self.toggle_layer(checked, p, z))

                tool_btn.setIconSize(THUMBNAIL_SIZE)
                tool_btn.setToolTip(img_name)
                self.thumbnail_buttons[img_path] = tool_btn
                
                grid_layout.addWidget(tool_btn, row, col)
                col += 1
                if col >= 7: # 7 columns max
                    col = 0; row += 1
                    
    def on_folder_btn_clicked(self, checked, clicked_btn, page_index):
        if checked:
            # Enforce radio-button like exclusivity
            for btn in self.folder_buttons:
                if btn != clicked_btn:
                    btn.setChecked(False)
            # Switch to this folder's page
            self.icon_stacked_widget.setCurrentIndex(page_index)
        else:
            # If user unclicks the currently active button, return to the empty page
            self.icon_stacked_widget.setCurrentIndex(0)

    def toggle_layer(self, checked, img_path, default_z_index):
        if checked:
            item = DraggableLayerItem(img_path)
            
            img_w = item.pil_img.width
            img_h = item.pil_img.height
            scale = min(self.canvas_w / img_w, self.canvas_h / img_h)
            
            item.update_transform(scale, 0.0) 
            
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
            item_data = list_item.data(Qt.UserRole)
            
            z_val = count - i 
            
            if item_data == "TEMPLATE_ITEM" and self.template_bg_item:
                self.template_bg_item.setZValue(z_val)
            elif item_data in self.active_layers:
                self.active_layers[item_data].setZValue(z_val)

    def on_selection_changed(self):
        selected_items = self.scene.selectedItems()
        if len(selected_items) == 1 and isinstance(selected_items[0], DraggableLayerItem):
            self._updating_ui = True
            item = selected_items[0]
            
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
        if not hasattr(self, 'current_template_path') or not self.current_template_path:
            QMessageBox.warning(self, "Export", "Please click a Base PSD template from the menu first.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Assembled PSD", "", "Photoshop Document (*.psd)")
        if not save_path: return

        try:
            from psd_tools import PSDImage
            psd_doc = PSDImage.open(self.current_template_path)

            count = self.layer_list.count()
            is_above_template = False
            bottom_insert_index = 0 

            for i in range(count - 1, -1, -1):
                list_item = self.layer_list.item(i)
                item_data = list_item.data(Qt.UserRole)
                
                if item_data == "TEMPLATE_ITEM":
                    is_above_template = True
                    continue
                    
                if item_data in self.active_layers:
                    item = self.active_layers[item_data]
                    pil_img = item.transformed_pil_img 
                    
                    new_layer = psd_doc.create_pixel_layer(
                        pil_img, 
                        name=os.path.basename(item.img_path), 
                        top=int(item.scenePos().y()), 
                        left=int(item.scenePos().x())
                    )
                    
                    if is_above_template:
                        psd_doc.append(new_layer)
                    else:
                        psd_doc.insert(bottom_insert_index, new_layer)
                        bottom_insert_index += 1

            psd_doc.save(save_path)
            QMessageBox.information(self, "Success", "Assembled PSD successfully saved!")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export PSD:\n{str(e)}")
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SimplePhotoshop()
    window.show()
    sys.exit(app.exec())