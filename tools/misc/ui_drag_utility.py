import sys
import random
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                               QGraphicsPixmapItem, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPainter

import re

# Configuration
BACKGROUND_IMAGE_PATH = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\interface\decisions\contest_for_mirkwood\cfw_bg.png'
OVERLAY_IMAGE_PATH = r'C:\Users\Kahl\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\gfx\interface\decisions\contest_for_mirkwood\cfm_numberdisplay_black.png'
INITIAL_COPIES = 3


ui_element_template = """
		iconType = {
			name = "disp_bg_$NUM$"
			spriteType = "GFX_cfm_numberdisplay"
			position = { x = $X_PLUS_0$ y = $Y_PLUS_0$ }
			Orientation = "UPPER_LEFT"
			pdx_tooltip = "state_$NUM$_presence_MIR"
		}

		instantTextboxType = {
			name = "disp_text_$NUM$"
			position = { x = $X_PLUS_25$ y = $Y_PLUS_10$ }
			font = "merienda_10"
			text = "testeroo_15p"
			maxWidth = 30
			maxHeight = 30
			fixedsize = yes
			format = left
			alwaystransparent = yes
		}

		iconType = {
			name = "disp_arrow_$NUM$"
			spriteType = "GFX_cfm_up_good"
			position = { x = $X_PLUS_42$ y = $Y_PLUS_5$ }
			Orientation = "UPPER_LEFT"
			alwaystransparent = yes
		}
"""



def process_coordinates(image_data_list):
    """
    This function is called when the button is pressed.
    
    Args:
        image_data_list (list): A list of dictionaries.
                                Example: [{'id': 1, 'x': 50.0, 'y': 100.0}, ...]
    """
    print(f"\n--- Processing {len(image_data_list)} images ---")
    
    for item in image_data_list:
        img_id = item['id']
        x = item['x']
        y = item['y']

        base_text = ui_element_template

        # 1. Replace the simple ID
        base_text = base_text.replace("$NUM$", str(img_id))

        # 2. Define a function to handle the coordinate math
        def calculate_replacement(match):
            # match.group(1) is 'X' or 'Y'
            # match.group(2) is 'PLUS' or 'MINUS'
            # match.group(3) is the integer (e.g., '15')
            
            axis = match.group(1)
            operation = match.group(2)
            offset = int(match.group(3))
            
            # Select the correct base coordinate
            base_val = x if axis == 'X' else y
            
            # Perform the math
            if operation == 'PLUS':
                result = base_val + offset
            else: # MINUS
                result = base_val - offset
                
            return str(result)

        # 3. Use Regex to find patterns and apply the function
        # Pattern explanation: Literal '$', followed by X or Y, then _PLUS_ or _MINUS_, then digits, then '$'
        pattern = r'\$([XY])_(PLUS|MINUS)_(\d+)\$'
        
        base_text = re.sub(pattern, calculate_replacement, base_text)

        # 4. Print result and continue
        print(base_text)



# ==========================================
#      GUI IMPLEMENTATION (PySide6)
# ==========================================

class DraggableImage(QGraphicsPixmapItem):
    def __init__(self, pixmap, img_id):
        super().__init__(pixmap)
        self.img_id = img_id
        # Enable dragging and selecting
        self.setFlags(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)
        self.setCacheMode(QGraphicsPixmapItem.CacheMode.DeviceCoordinateCache)

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Draggable Image Tool")
        self.resize(900, 700)
        self.counter = 0

        # Layouts
        self.main_layout = QVBoxLayout(self)
        self.controls_layout = QHBoxLayout()

        # 1. Setup Graphics Scene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.main_layout.addWidget(self.view)
        self.main_layout.addLayout(self.controls_layout)

        # 2. Buttons
        self.btn_add = QPushButton("Add New Image")
        self.btn_add.clicked.connect(self.add_single_overlay)
        self.controls_layout.addWidget(self.btn_add)

        self.btn_process = QPushButton("Process Coordinates")
        self.btn_process.clicked.connect(self.gather_and_send_coordinates)
        self.controls_layout.addWidget(self.btn_process)

        # 3. Load Images
        self.draggable_items = []
        self.bg_pixmap = self._load_pixmap(BACKGROUND_IMAGE_PATH, is_bg=True)
        self.overlay_pixmap = self._load_pixmap(OVERLAY_IMAGE_PATH, is_bg=False)

        # 4. Initialize
        self.setup_scene()
        for _ in range(INITIAL_COPIES):
            self.add_single_overlay()

    def _load_pixmap(self, path, is_bg=False):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            if is_bg:
                pixmap = QPixmap(800, 600)
                pixmap.fill(QColor("#e0e0e0"))
            else:
                pixmap = QPixmap(50, 50)
                pixmap.fill(QColor("#3498db"))
        return pixmap

    def setup_scene(self):
        self.scene.setSceneRect(0, 0, self.bg_pixmap.width(), self.bg_pixmap.height())
        bg_item = QGraphicsPixmapItem(self.bg_pixmap)
        bg_item.setZValue(-1) # Send to back
        self.scene.addItem(bg_item)

    def add_single_overlay(self):
        self.counter += 1
        item = DraggableImage(self.overlay_pixmap, img_id=self.counter)
        
        # Place randomly within bounds
        max_x = max(0, int(self.scene.width() - self.overlay_pixmap.width()))
        max_y = max(0, int(self.scene.height() - self.overlay_pixmap.height()))
        
        item.setPos(random.randint(0, max_x), random.randint(0, max_y))
        
        self.scene.addItem(item)
        self.draggable_items.append(item)

    def gather_and_send_coordinates(self):
        """
        Collects data from the GUI items and sends it to the user-defined function.
        """
        data_packet = []
        
        # Sort items by ID so the list order is consistent
        sorted_items = sorted(self.draggable_items, key=lambda x: x.img_id)

        for item in sorted_items:
            pos = item.pos()
            # Construct a dictionary for each item
            item_data = {
                'id': item.img_id,
                'x': pos.x(),
                'y': pos.y()
            }
            data_packet.append(item_data)

        # CALL THE TOP FUNCTION
        process_coordinates(data_packet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())