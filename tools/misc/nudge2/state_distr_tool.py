import sys
import numpy as np
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout, 
    QVBoxLayout, QScrollArea, QFrame, QPushButton
)
from PySide6.QtGui import QPixmap, QColor, QFont
from PySide6.QtCore import Qt

from definitioncsv import *

from pathlib import Path

class ImageAnalyzer:
    """Helper class to handle image processing logic."""
    
    @staticmethod
    def find_color_centroids(image_path, target_colors):
        """
        Loads an image and calculates the center (centroid) of pixels 
        for each color in the target_colors list.
        """
        # Load image using Pillow
        try:
            pil_img = Image.open(image_path).convert('RGB')
        except FileNotFoundError:
            return None, []

        # Convert to NumPy array for fast processing
        # Array shape is (Height, Width, 3)
        img_array = np.array(pil_img)
        
        results = []

        for color in target_colors:
            # Create a mask where the image pixels match the target color
            # exact match requires [R, G, B] equality
            mask = np.all(img_array == color, axis=-1)
            
            # Get coordinates of all matching pixels (returns indices: rows/y, cols/x)
            y_indices, x_indices = np.where(mask)
            
            if len(x_indices) > 0:
                # Calculate the mean (centroid)
                center_x = int(np.mean(x_indices))
                center_y = int(np.mean(y_indices))
                results.append({
                    "color": color,
                    "position": (center_x, center_y),
                    "count": len(x_indices) # number of pixels found
                })
        
        return pil_img, results

class OverlayMarker(QPushButton):
    """A clickable UI text element placed on the map."""
    def __init__(self, parent, data, on_click_callback):
        super().__init__(parent)
        self.data = data
        self.clicked_callback = on_click_callback
        
        # UI Appearance
        r, g, b = data['color']
        contrast_color = "black" if (r*0.299 + g*0.587 + b*0.114) > 186 else "white"
        
        self.setText(f"({r},{g},{b})")
        self.setFont(QFont("Arial", 8, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        
        # Style: Rounded badge with the background color matching the target
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({r}, {g}, {b});
                color: {contrast_color};
                border: 2px solid white;
                border-radius: 10px;
                padding: 5px;
            }}
            QPushButton:hover {{
                border: 2px solid #FFD700; /* Gold border on hover */
            }}
        """)
        
        # Adjust size to fit text
        self.adjustSize()
        
        # Connect click event
        self.clicked.connect(lambda: self.clicked_callback(self.data))

class PropertiesPanel(QFrame):
    """Side panel to display details of the selected element."""
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedWidth(250)
        self.setStyleSheet("background-color: #f0f0f0; border-left: 1px solid #ccc;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title = QLabel("Properties")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Details Labels
        self.lbl_color = QLabel("Color: -")
        self.lbl_pos = QLabel("Position: -")
        self.lbl_count = QLabel("Pixel Count: -")
        
        layout.addWidget(self.lbl_color)
        layout.addWidget(self.lbl_pos)
        layout.addWidget(self.lbl_count)
        
        layout.addStretch()

    def update_info(self, data):
        c = data['color']
        pos = data['position']
        count = data['count']
        
        self.lbl_color.setText(f"Color: RGB({c[0]}, {c[1]}, {c[2]})")
        self.lbl_pos.setText(f"Centroid: ({pos[0]}, {pos[1]})")
        self.lbl_count.setText(f"Pixels found: {count}")

class MainWindow(QMainWindow):
    def __init__(self, image_path, colors):
        super().__init__()
        self.setWindowTitle("Color Centroid Visualizer")
        self.resize(1000, 700)
        
        # 1. Process Data
        pil_img, self.markers_data = ImageAnalyzer.find_color_centroids(image_path, colors)
        
        if pil_img is None:
            self.show_error(f"Could not load image: {image_path}")
            return

        # 2. Setup Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 3. Image Area (Scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Container for Image + Overlays
        self.image_container = QWidget()
        self.image_container.setFixedSize(pil_img.width, pil_img.height)
        
        # Background Image Label
        self.bg_label = QLabel(self.image_container)
        self.bg_label.setPixmap(QPixmap(image_path))
        self.bg_label.setGeometry(0, 0, pil_img.width, pil_img.height)
        
        scroll_area.setWidget(self.image_container)
        
        # 4. Properties Panel
        self.props_panel = PropertiesPanel()
        
        # Add to layout
        main_layout.addWidget(scroll_area, 1) # 1 = stretch factor
        main_layout.addWidget(self.props_panel)
        
        # 5. Create Overlay Elements
        self.create_overlays()

    def create_overlays(self):
        for data in self.markers_data:
            # Create the marker widget
            marker = OverlayMarker(self.image_container, data, self.on_marker_clicked)
            marker.show()
            
            # Position it. Note: 'pos' is the center. 
            # We must subtract half width/height to center the widget over that point.
            cx, cy = data['position']
            w = marker.width()
            h = marker.height()
            marker.move(cx - w//2, cy - h//2)

    def on_marker_clicked(self, data):
        """Slot called when a marker is clicked."""
        self.props_panel.update_info(data)

    def show_error(self, message):
        lbl = QLabel(message, self)
        lbl.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(lbl)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- CONFIGURATION ---
    # 1. Ensure you have an image named 'image.png' in the folder, or change this path.
    IMAGE_PATH = Path.cwd() / "tools/misc/nudge2/states_view.png"
    
    # 2. Define the list of RGB colors you want to find.
    # Format: (Red, Green, Blue)
    TARGET_COLORS = [ ]
    # ---------------------

    states = get_all_states()
    for st in states:
        if st.owner != "MIR": continue
        col = get_color_from_seed(str(st.state_id))
        TARGET_COLORS.append(col)

    window = MainWindow(IMAGE_PATH, TARGET_COLORS)
    window.show()
    
    sys.exit(app.exec())