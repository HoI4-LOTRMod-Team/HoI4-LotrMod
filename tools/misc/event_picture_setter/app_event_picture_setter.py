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

# --- Hard-coded Paths ---
LOCS_PATH = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\localisation'
EVENTS_FILE = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\events\DolGuldur.txt'
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
    """Helper function to load a DDS file via Pillow and convert to QPixmap."""
    if not os.path.exists(filepath):
        return QPixmap()
    try:
        with Image.open(filepath) as img:
            img = img.convert("RGBA") # Ensure compatibility
            qim = ImageQt(img)
            pixmap = QPixmap.fromImage(qim)
            if max_size:
                pixmap = pixmap.scaled(max_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            return pixmap
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return QPixmap()

class EventImageTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Image Assignment Tool")
        # Increased window width to give the gallery more room
        self.resize(1200, 600) 
        
        self.current_index = 0
        
        # --- UI Setup ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # -- Left Panel (Event Info & Current Image) --
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
        
        # -- Right Panel (Image Gallery) --
        self.image_gallery = QListWidget()
        self.image_gallery.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_gallery.setIconSize(QSize(100, 100)) # Slightly smaller icons
        
        # Enforce a strict grid so long text doesn't ruin the columns
        self.image_gallery.setGridSize(QSize(130, 140)) 
        
        self.image_gallery.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.image_gallery.setMovement(QListWidget.Movement.Static) # Prevents dragging items
        self.image_gallery.setSpacing(5)
        
        # Give the gallery enough minimum width to fit 4 columns of 130px (520px + scrollbar)
        self.image_gallery.setMinimumWidth(550) 
        
        self.image_gallery.itemDoubleClicked.connect(self.assign_image)
        
        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addWidget(self.image_gallery)
        
        # Initialize
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
                
                # Set tooltips so the user can see the full ID if it gets truncated by the grid
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
        
        # Text
        self.title_label.setText(self.get_localized_string(current_event, "title"))
        self.desc_label.setText(self.get_localized_string(current_event, "desc"))
        self.next_button.setText(f"Next Event ({self.current_index + 1} / {len(events_list)})")
        
        # Picture
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

    def assign_image(self, item):
        if not events_list:
            return
            
        new_gfx_id = item.data(Qt.ItemDataRole.UserRole)
        current_event = events_list[self.current_index]
        has_picture = current_event.Has("picture")
        
        if new_gfx_id is None:
            if has_picture:
                current_event.Remove("picture")
        else:
            if has_picture:
                current_event.Get("picture").value = new_gfx_id
            else:
                # Updated insertion index from 4 to 1
                current_event.InsertAt(f"picture = {new_gfx_id}", 1) 
                
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