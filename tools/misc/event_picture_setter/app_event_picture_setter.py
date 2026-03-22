import sys
import os
import glob
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QListWidget, 
                               QListWidgetItem, QMessageBox)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
from PIL import Image
from PIL.ImageQt import ImageQt

import io
from PySide6.QtWidgets import QDialog, QLineEdit, QFileDialog
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import QBuffer, QIODevice
from PIL import ImageOps

# --- Hard-coded Paths ---
LOCS_PATH = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\localisation'
EVENTS_FILE = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\events\MirkwoodStory.txt'
IMAGES_PATH = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\event_pictures\report_events\unmasked'


# --- Pre-programmed Libraries ---
from loc_collection import LocCollection
from pdx_parser import *

# --- Data Initialization ---
locs = LocCollection(LOCS_PATH)
# Caching the root PObj as requested
events_obj = ParseListFromFile_asPObj(EVENTS_FILE)
events_list = events_obj.GetAll("country_event").value


def load_dds_pixmap(filepath, max_size=None):
    if not os.path.exists(filepath):
        return QPixmap()
    try:
        with Image.open(filepath) as img:
            img = img.convert("RGBA")
            qim = ImageQt(img)
            pixmap = QPixmap.fromImage(qim)
            if max_size:
                pixmap = pixmap.scaled(max_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            return pixmap
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return QPixmap()


class AddImageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Event Image")
        self.resize(400, 350)
        
        self.pil_image = None
        self.new_gfx_id = None # We will store the generated ID here
        
        layout = QVBoxLayout(self)
        
        self.name_input = QLineEdit("report_event_new_image")
        layout.addWidget(QLabel("Image Name (without .dds):"))
        layout.addWidget(self.name_input)
        
        self.preview_label = QLabel("Paste (Ctrl+V) or Browse for an image")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(210, 176)
        self.preview_label.setStyleSheet("border: 2px dashed #aaa; background-color: #222;")
        layout.addWidget(self.preview_label, stretch=1)
        
        button_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Browse File")
        self.browse_btn.clicked.connect(self.browse_image)
        self.paste_btn = QPushButton("Paste from Clipboard")
        self.paste_btn.clicked.connect(self.paste_image)
        
        button_layout.addWidget(self.browse_btn)
        button_layout.addWidget(self.paste_btn)
        layout.addLayout(button_layout)
        
        self.save_btn = QPushButton("Process and Save")
        self.save_btn.setStyleSheet("background-color: #1976d2; color: white; font-weight: bold;")
        self.save_btn.clicked.connect(self.process_and_accept)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

        shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        shortcut.activated.connect(self.paste_image)

    def load_from_pil(self, img):
        self.pil_image = img.convert("RGBA")
        qim = ImageQt(self.pil_image)
        pixmap = QPixmap.fromImage(qim).scaled(
            210, 176, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.preview_label.setPixmap(pixmap)
        self.save_btn.setEnabled(True)

    def browse_image(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if filepath:
            try:
                img = Image.open(filepath)
                self.load_from_pil(img)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not load image:\n{e}")

    def paste_image(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasImage():
            qimage = clipboard.image()
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.ReadWrite)
            qimage.save(buffer, "PNG")
            img = Image.open(io.BytesIO(buffer.data().data()))
            self.load_from_pil(img)
        else:
            QMessageBox.information(self, "No Image", "No image found in clipboard.")

    def process_and_accept(self):
        if not self.pil_image:
            return
            
        filename = self.name_input.text().strip()
        if not filename:
            QMessageBox.warning(self, "Error", "Please provide a name for the image.")
            return
            
        if not filename.endswith(".dds"):
            filename += ".dds"
            
        save_path = os.path.join(IMAGES_PATH, filename)
        
        try:
            processed_img = ImageOps.fit(self.pil_image, (210, 176), method=Image.Resampling.LANCZOS)
            if processed_img.mode != "RGBA":
                processed_img = processed_img.convert("RGB")
                
            processed_img.save(save_path, format="DDS")
            
            # Save the GFX ID so the main window can use it!
            self.new_gfx_id = "GFX_" + filename.replace(".dds", "")
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save DDS:\n{e}")


class EventImageTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Image Assignment Tool")
        self.resize(1200, 600)
        
        self.current_index = 0
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # -- Left Panel --
        left_panel = QVBoxLayout()
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 5px;")
        
        self.desc_label = QLabel()
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        
        self.current_image_label = QLabel()
        self.current_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_image_label.setMinimumSize(400, 300)
        self.current_image_label.setStyleSheet("border: 1px solid #aaa; background-color: #333;")
        
        self.next_button = QPushButton("Next Event")
        self.next_button.setMinimumHeight(40)
        self.next_button.clicked.connect(self.next_event)

        self.save_button = QPushButton("Save Changes to File")
        self.save_button.setMinimumHeight(40)
        self.save_button.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
        self.save_button.clicked.connect(self.save_file)
        
        left_panel.addWidget(self.title_label)
        left_panel.addWidget(self.desc_label)
        left_panel.addWidget(self.current_image_label, stretch=1)
        left_panel.addWidget(self.next_button)
        left_panel.addWidget(self.save_button)
        
        # -- Right Panel --
        right_panel = QVBoxLayout()
        
        self.add_image_btn = QPushButton("+ Add New Image")
        self.add_image_btn.setMinimumHeight(35)
        self.add_image_btn.setStyleSheet("background-color: #5e35b1; color: white; font-weight: bold;")
        self.add_image_btn.clicked.connect(self.open_add_image_dialog)
        
        self.image_gallery = QListWidget()
        self.image_gallery.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_gallery.setIconSize(QSize(100, 100))
        self.image_gallery.setGridSize(QSize(130, 140))
        self.image_gallery.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.image_gallery.setMovement(QListWidget.Movement.Static)
        self.image_gallery.setSpacing(5)
        self.image_gallery.setMinimumWidth(550)
        self.image_gallery.itemDoubleClicked.connect(self.on_gallery_double_click)
        
        right_panel.addWidget(self.add_image_btn)
        right_panel.addWidget(self.image_gallery)
        
        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addLayout(right_panel)
        
        self.populate_gallery()
        self.update_ui()

    def populate_gallery(self):
        none_item = QListWidgetItem("None")
        none_item.setData(Qt.ItemDataRole.UserRole, None)
        self.image_gallery.addItem(none_item)
        
        if not os.path.exists(IMAGES_PATH):
            return

        search_pattern = os.path.join(IMAGES_PATH, "*.dds")
        for filepath in glob.glob(search_pattern):
            filename = os.path.basename(filepath)
            gfx_id = "GFX_" + filename.replace(".dds", "")
            
            pixmap = load_dds_pixmap(filepath, QSize(100, 100))
            if not pixmap.isNull():
                item = QListWidgetItem(QIcon(pixmap), gfx_id)
                item.setData(Qt.ItemDataRole.UserRole, gfx_id)
                item.setToolTip(gfx_id)
                self.image_gallery.addItem(item)

    def get_localized_string(self, event, key):
        if event.Has(key):
            loc_id = str(event.Get(key).value)
            if loc_id in locs._data:
                return str(locs._data[loc_id])
        return "-- undefined --"

    def update_ui(self):
        if not events_list:
            return
            
        current_event = events_list[self.current_index]
        self.title_label.setText(self.get_localized_string(current_event, "title"))
        self.desc_label.setText(self.get_localized_string(current_event, "desc"))
        self.next_button.setText(f"Next Event ({self.current_index + 1} / {len(events_list)})")
        
        self.current_image_label.clear()
        self.current_image_label.setText("No Image")
        
        if current_event.Has("picture"):
            gfx_id = str(current_event.Get("picture").value)
            filename = gfx_id.replace("GFX_", "") + ".dds"
            filepath = os.path.join(IMAGES_PATH, filename)
            
            pixmap = load_dds_pixmap(filepath, QSize(400, 300))
            if not pixmap.isNull():
                self.current_image_label.setPixmap(pixmap)
            else:
                self.current_image_label.setText(f"Image not found:\n{filename}")

    def set_event_image(self, new_gfx_id):
        """Helper method to apply an image ID to the current event."""
        if not events_list: return
        
        current_event = events_list[self.current_index]
        has_picture = current_event.Has("picture")
        
        if new_gfx_id is None:
            if has_picture:
                current_event.Remove("picture")
        else:
            if has_picture:
                current_event.Get("picture").value = new_gfx_id
            else:
                current_event.InsertAt(f"picture = {new_gfx_id}", 1)

    def on_gallery_double_click(self, item):
        new_gfx_id = item.data(Qt.ItemDataRole.UserRole)
        self.set_event_image(new_gfx_id)
        self.update_ui()

    def open_add_image_dialog(self):
        dialog = AddImageDialog(self)
        if dialog.exec():
            # Apply the newly generated image to the current event
            if dialog.new_gfx_id:
                self.set_event_image(dialog.new_gfx_id)
            
            # Refresh gallery and UI
            self.image_gallery.clear()
            self.populate_gallery()
            self.update_ui()

    def next_event(self):
        if events_list:
            self.current_index = (self.current_index + 1) % len(events_list)
            self.update_ui()

    def save_file(self):
        try:
            SaveObjValueToFile(events_obj, EVENTS_FILE)
            QMessageBox.information(self, "Success", "Events file saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EventImageTool()
    window.show()
    sys.exit(app.exec())