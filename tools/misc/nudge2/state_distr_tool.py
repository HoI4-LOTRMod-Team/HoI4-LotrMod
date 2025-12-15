import sys
import numpy as np
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout, 
    QVBoxLayout, QFrame, QPushButton, QSpinBox, QComboBox,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QStackedWidget,
    QGridLayout, QScrollArea
)
from PySide6.QtGui import QPixmap, QColor, QFont, QPainter
from PySide6.QtCore import Qt
from pathlib import Path

# --- RESTORED IMPORTS ---
# We assume definitioncsv exists in your directory
from definitioncsv import * # --- CONSTANTS ---
MODE_MANPOWER = "Manpower"
MODE_INFRASTRUCTURE = "Infrastructure"
MODE_ARMS = "Arms Factory"
MODE_INDUSTRY = "Industrial Complex"
MODE_CATEGORY = "State Category"
MODE_RESOURCES = "Resources"

CATEGORIES = [
    "wasteland", "enclave", "tiny_island", "pastoral", "rural", 
    "town", "large_town", "city", "large_city", "metropolis", "megalopolis"
]

# Resource IDs and their short display names
RESOURCE_TYPES = ["oil", "aluminium", "rubber", "tungsten", "steel", "chromium", "coal"]
RESOURCE_SHORTS = {
    "oil": "oil", "aluminium": "alu", "rubber": "rub", 
    "tungsten": "tun", "steel": "ste", "chromium": "chr", "coal": "coa"
}

def format_k(value):
    """Format large numbers (e.g. 12500 -> 12.5k)."""
    if isinstance(value, (int, float)):
        if value >= 1000:
            return f"{value/1000:.1f}k"
    return str(value)

class ImageAnalyzer:
    """Helper class to handle image processing logic."""
    @staticmethod
    def analyze_states(image_path, target_data):
        try:
            pil_img = Image.open(image_path).convert('RGB')
        except FileNotFoundError:
            return None, []

        img_array = np.array(pil_img)
        results = []
        total_pixels_all_selected = 0

        # Helper to get numeric value safely
        def get_val(obj, default=0):
            try: return int(obj.value)
            except: return default

        # Helper to get string value safely
        def get_str(obj, default=""):
            try: return str(obj.value)
            except: return default

        for item in target_data:
            color = item['color']
            state_obj = item['state']
            
            mask = np.all(img_array == color, axis=-1)
            y_indices, x_indices = np.where(mask)
            count = len(x_indices)
            
            if count > 0:
                total_pixels_all_selected += count
                center_x = int(np.mean(x_indices))
                center_y = int(np.mean(y_indices))
                
                # --- DATA EXTRACTION ---
                
                # 1. Manpower
                try: mp_val = get_val(state_obj.pObj.Get("manpower"))
                except: mp_val = 0

                # 2. Buildings
                infra_val, arms_val, ind_val = 0, 0, 0
                try:
                    buildings = state_obj.pObj.Get("history").Get("buildings")
                    infra_val = get_val(buildings.Get("infrastructure"))
                    arms_val = get_val(buildings.Get("arms_factory"))
                    ind_val = get_val(buildings.Get("industrial_complex"))
                except:
                    pass

                # 3. Category
                try: cat_val = get_str(state_obj.pObj.Get("state_category"), "rural")
                except: cat_val = "rural"

                # 4. Resources
                res_dict = {}
                res_total = 0
                try:
                    res_obj = state_obj.pObj.Get("resources")
                    for r_type in RESOURCE_TYPES:
                        val = 0
                        if res_obj.Has(r_type):
                            try:
                                # Specific float->int conversion as requested
                                val = int(float(res_obj.Get(r_type).value))
                            except:
                                val = 0
                        res_dict[r_type] = val
                        res_total += val
                except:
                    # If resources block is missing completely
                    for r_type in RESOURCE_TYPES: res_dict[r_type] = 0

                results.append({
                    "state": state_obj,
                    "color": color,
                    "position": (center_x, center_y),
                    "count": count,
                    "area_percentage": 0.0,
                    
                    "manpower": mp_val,
                    "infrastructure": infra_val,
                    "arms_factory": arms_val,
                    "industrial_complex": ind_val,
                    "state_category": cat_val,
                    "resources": res_dict,
                    "resources_total": res_total,
                    
                    "percentage_share": 0.0 
                })

        if total_pixels_all_selected > 0:
            for res in results:
                res['area_percentage'] = (res['count'] / total_pixels_all_selected) * 100.0
        
        return pil_img, results

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

class OverlayMarker(QPushButton):
    def __init__(self, data, on_click_callback):
        super().__init__()
        self.data = data
        self.clicked_callback = on_click_callback
        
        r, g, b = data['color']
        self.contrast_color = "black" if (r*0.299 + g*0.587 + b*0.114) > 186 else "white"
        
        self.setFont(QFont("Arial", 8, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({r}, {g}, {b});
                color: {self.contrast_color};
                border: 2px solid white;
                border-radius: 10px;
                padding: 4px 8px;
                text-align: center;
            }}
            QPushButton:hover {{
                border: 2px solid #FFD700;
            }}
        """)
        
        self.clicked.connect(lambda: self.clicked_callback(self.data))

    def refresh_text(self, mode):
        """Updates the text based on current data values and mode."""
        
        val_str = "?"
        show_share = True

        if mode == MODE_CATEGORY:
            val_str = self.data.get('state_category', 'rural')
            self.setText(val_str)
            self.adjustSize()
            return
        
        elif mode == MODE_RESOURCES:
            # Build string like "5rub, 3chr"
            parts = []
            res_data = self.data.get('resources', {})
            # Sort for consistent order or use list order
            for r_type in RESOURCE_TYPES:
                val = res_data.get(r_type, 0)
                if val > 0:
                    short = RESOURCE_SHORTS.get(r_type, r_type[:3])
                    parts.append(f"{val}{short}")
            
            if not parts:
                val_str = "-"
            else:
                val_str = ", ".join(parts)
                # Break lines if too long?
                if len(val_str) > 15:
                    val_str = val_str.replace(", ", "\n")
            
            # For resources, we might still show percentage share of global resources?
            # Or just the raw values. Let's show just values as it gets crowded.
            show_share = False 

        elif mode == MODE_MANPOWER:
            val = self.data['manpower']
            val_str = format_k(val)
        elif mode == MODE_INFRASTRUCTURE:
            val_str = str(self.data['infrastructure'])
        elif mode == MODE_ARMS:
            val_str = str(self.data['arms_factory'])
        elif mode == MODE_INDUSTRY:
            val_str = str(self.data['industrial_complex'])

        if show_share:
            perc = self.data['percentage_share']
            self.setText(f"{val_str}\n{perc:.0f}%")
        else:
            self.setText(val_str)
            
        self.adjustSize()

class ResourceEditorWidget(QWidget):
    """Sub-widget for editing 7 distinct resource values."""
    def __init__(self, parent_callback):
        super().__init__()
        self.parent_callback = parent_callback
        self.spinboxes = {}
        
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a spinbox for each resource type
        for idx, r_type in enumerate(RESOURCE_TYPES):
            lbl = QLabel(r_type.title() + ":")
            lbl.setFont(QFont("Arial", 9))
            
            sb = QSpinBox()
            sb.setRange(0, 9999)
            sb.setSingleStep(1)
            # Store type in the widget for the callback
            sb.setProperty("resource_type", r_type)
            sb.valueChanged.connect(self.on_val_changed)
            
            self.spinboxes[r_type] = sb
            
            layout.addWidget(lbl, idx, 0)
            layout.addWidget(sb, idx, 1)

    def on_val_changed(self, val):
        sender = self.sender()
        r_type = sender.property("resource_type")
        self.parent_callback(r_type, val)

    def load_values(self, res_dict):
        for r_type, sb in self.spinboxes.items():
            sb.blockSignals(True)
            sb.setValue(res_dict.get(r_type, 0))
            sb.blockSignals(False)

class PropertiesPanel(QFrame):
    def __init__(self, on_value_change_callback, on_mode_change_callback):
        super().__init__()
        self.on_value_change = on_value_change_callback
        self.on_mode_change = on_mode_change_callback
        self.current_data = None
        self.is_updating_ui = False 
        self.current_mode = MODE_MANPOWER

        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedWidth(250)
        self.setStyleSheet("background-color: #f0f0f0; border-left: 1px solid #ccc;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        
        # --- Mode Selection ---
        lbl_mode = QLabel("Editing Mode:")
        lbl_mode.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(lbl_mode)
        
        self.combo_mode = QComboBox()
        self.combo_mode.addItems([
            MODE_MANPOWER, 
            MODE_INFRASTRUCTURE,
            MODE_ARMS,
            MODE_INDUSTRY,
            MODE_CATEGORY,
            MODE_RESOURCES
        ])
        self.combo_mode.currentTextChanged.connect(self.on_mode_changed_internal)
        layout.addWidget(self.combo_mode)
        
        layout.addSpacing(10)
        
        # --- Global Stats ---
        self.lbl_total_global = QLabel("Total: 0")
        self.lbl_total_global.setFont(QFont("Arial", 10, QFont.Bold))
        self.lbl_total_global.setStyleSheet("color: #333; padding: 5px; border: 1px solid #aaa; background: white;")
        layout.addWidget(self.lbl_total_global)

        layout.addSpacing(10)
        
        title = QLabel("Selected State")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        self.lbl_id = QLabel("ID: -")
        self.lbl_owner = QLabel("Owner: -")
        self.lbl_color = QLabel("Color: -")
        self.lbl_area_stats = QLabel("Area: -")
        self.lbl_share_stats = QLabel("Share: -")
        
        for lbl in [self.lbl_id, self.lbl_owner, self.lbl_color, self.lbl_area_stats, self.lbl_share_stats]:
            lbl.setStyleSheet("padding: 2px 0;")
            layout.addWidget(lbl)
            
        layout.addSpacing(10)
        self.lbl_edit = QLabel("Edit Value:")
        self.lbl_edit.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.lbl_edit)

        # --- Stacked Widget for Inputs ---
        self.input_stack = QStackedWidget()
        
        # 1. Spinbox for single numbers
        self.spin_value = QSpinBox()
        self.spin_value.valueChanged.connect(self.on_spinbox_changed)
        self.input_stack.addWidget(self.spin_value)
        
        # 2. Combobox for Categories
        self.combo_category = QComboBox()
        self.combo_category.addItems(CATEGORIES)
        self.combo_category.currentTextChanged.connect(self.on_category_changed)
        self.input_stack.addWidget(self.combo_category)

        # 3. Resources Editor (Scrollable if screen small, but 7 items fit fine)
        self.res_editor = ResourceEditorWidget(self.on_resource_changed)
        self.input_stack.addWidget(self.res_editor)
        
        layout.addWidget(self.input_stack)
        
        layout.addStretch()
        
        self.update_ui_mode_state()

    def update_ui_mode_state(self):
        """Adjusts inputs and labels based on mode."""
        self.spin_value.blockSignals(True)
        
        # Visibility Logic
        if self.current_mode == MODE_CATEGORY:
            self.input_stack.setCurrentWidget(self.combo_category)
            self.lbl_total_global.setVisible(False)
            self.lbl_share_stats.setVisible(False)
        elif self.current_mode == MODE_RESOURCES:
            self.input_stack.setCurrentWidget(self.res_editor)
            self.lbl_total_global.setVisible(True) # Show total resource units globally
            self.lbl_share_stats.setVisible(False) # Share is ambiguous for multiple resources
        else:
            self.input_stack.setCurrentWidget(self.spin_value)
            self.lbl_total_global.setVisible(True)
            self.lbl_share_stats.setVisible(True)

            # Constraints for spinbox
            if self.current_mode == MODE_MANPOWER:
                self.spin_value.setRange(0, 99999999)
                self.spin_value.setSingleStep(100)
            elif self.current_mode == MODE_INFRASTRUCTURE:
                self.spin_value.setRange(0, 5)
                self.spin_value.setSingleStep(1)
            else: 
                self.spin_value.setRange(0, 100)
                self.spin_value.setSingleStep(1)

        self.spin_value.blockSignals(False)

    def on_mode_changed_internal(self, text):
        self.current_mode = text
        self.update_ui_mode_state()
        self.on_mode_change(text)

    def update_global_total(self, total_val):
        if self.current_mode == MODE_CATEGORY:
            return 
            
        formatted = format_k(total_val) if self.current_mode == MODE_MANPOWER else str(total_val)
        label_txt = f"Total {self.current_mode}:"
        if self.current_mode == MODE_RESOURCES:
            label_txt = "Total Units:"
        
        self.lbl_total_global.setText(f"{label_txt} {formatted}")

    def update_info(self, data):
        self.current_data = data
        self.is_updating_ui = True
        
        st = data['state']
        c = data['color']
        
        self.lbl_id.setText(f"ID: {st.state_id}")
        self.lbl_owner.setText(f"Owner: {st.owner}")
        self.lbl_color.setText(f"Color: RGB{c}")
        self.lbl_area_stats.setText(f"Area: {data['count']} px ({data['area_percentage']:.1f}%)")
        self.lbl_share_stats.setText(f"Group Share: {data['percentage_share']:.1f}%")
        
        # Populate Inputs
        if self.current_mode == MODE_CATEGORY:
            current_cat = data.get('state_category', 'rural')
            idx = self.combo_category.findText(current_cat)
            self.combo_category.setCurrentIndex(max(0, idx))
            
        elif self.current_mode == MODE_RESOURCES:
            # Load dictionary into the 7 spinboxes
            self.res_editor.load_values(data.get('resources', {}))
            
        else:
            # Numeric modes
            key_map = {
                MODE_MANPOWER: 'manpower',
                MODE_INFRASTRUCTURE: 'infrastructure',
                MODE_ARMS: 'arms_factory',
                MODE_INDUSTRY: 'industrial_complex'
            }
            key = key_map.get(self.current_mode, 'manpower')
            self.spin_value.setValue(data.get(key, 0))
        
        self.is_updating_ui = False

    def on_spinbox_changed(self, value):
        if self.is_updating_ui or self.current_data is None: return
        
        st = self.current_data['state']
        try:
            if self.current_mode == MODE_MANPOWER:
                self.current_data['manpower'] = value
                st.pObj.Get("manpower").value = str(value)
            elif self.current_mode == MODE_INFRASTRUCTURE:
                self.current_data['infrastructure'] = value
                st.pObj.Get("history").Get("buildings").Get("infrastructure").value = str(value)
            elif self.current_mode == MODE_ARMS:
                self.current_data['arms_factory'] = value
                st.pObj.Get("history").Get("buildings").Get("arms_factory").value = str(value)
            elif self.current_mode == MODE_INDUSTRY:
                self.current_data['industrial_complex'] = value
                st.pObj.Get("history").Get("buildings").Get("industrial_complex").value = str(value)
                
            self.on_value_change()
        except Exception as e:
            print(f"Update failed: {e}")

    def on_category_changed(self, value_text):
        if self.is_updating_ui or self.current_data is None: return
        try:
            self.current_data['state_category'] = value_text
            self.current_data['state'].pObj.Get("state_category").value = value_text
            self.on_value_change()
        except Exception as e:
            print(f"Category update failed: {e}")

    def on_resource_changed(self, r_type, value):
        if self.is_updating_ui or self.current_data is None: return
        
        try:
            st_obj = self.current_data['state']
            res_obj = st_obj.pObj.Get("resources") # Assume resources block exists
            
            # Update internal dictionary
            self.current_data['resources'][r_type] = value
            
            # Update external Object
            if value > 0:
                if res_obj.Has(r_type):
                    # Direct update
                    res_obj.Get(r_type).value = str(value)
                else:
                    # Insert new definition
                    res_obj.Insert(f"{r_type} = {value}")
            else:
                # Value is 0
                if res_obj.Has(r_type):
                    # Remove definition
                    res_obj.Remove(r_type)
            
            # Recalculate total for this state (just sum of units)
            self.current_data['resources_total'] = sum(self.current_data['resources'].values())
            
            self.on_value_change()
        except Exception as e:
            print(f"Resource update failed: {e}")

class MainWindow(QMainWindow):
    def __init__(self, image_path, target_data):
        super().__init__()
        self.setWindowTitle("State Distribution Tool")
        self.resize(1100, 750)
        self.current_mode = MODE_MANPOWER
        self.markers_widgets = [] 
        
        # 1. Process Data
        pil_img, self.markers_data = ImageAnalyzer.analyze_states(image_path, target_data)
        
        self.recalculate_stats()

        if pil_img is None:
            self.show_error(f"Could not load image: {image_path}")
            return

        # 2. Layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        
        self.pixmap_item = QGraphicsPixmapItem(QPixmap(str(image_path)))
        self.scene.addItem(self.pixmap_item)
        
        self.props_panel = PropertiesPanel(
            on_value_change_callback=self.on_data_changed,
            on_mode_change_callback=self.on_mode_changed
        )
        
        main_layout.addWidget(self.view, 1)
        main_layout.addWidget(self.props_panel)
        
        self.create_overlays()
        
        self.update_global_total_label()

    def recalculate_stats(self):
        """Recalculates percentage shares."""
        if self.current_mode == MODE_CATEGORY:
            return 0 

        # Determine total sum based on mode
        total = 0
        if self.current_mode == MODE_RESOURCES:
            # Sum of all resource units everywhere
            total = sum(item['resources_total'] for item in self.markers_data)
        else:
            key_map = {
                MODE_MANPOWER: 'manpower',
                MODE_INFRASTRUCTURE: 'infrastructure',
                MODE_ARMS: 'arms_factory',
                MODE_INDUSTRY: 'industrial_complex'
            }
            key = key_map.get(self.current_mode)
            total = sum(item[key] for item in self.markers_data)
        
        # Calculate shares (only relevant for numeric single-value modes)
        if self.current_mode != MODE_RESOURCES:
            key = key_map.get(self.current_mode)
            for item in self.markers_data:
                if total > 0:
                    item['percentage_share'] = (item[key] / total) * 100.0
                else:
                    item['percentage_share'] = 0.0
        
        return total

    def update_global_total_label(self):
        total = self.recalculate_stats()
        self.props_panel.update_global_total(total)

    def on_mode_changed(self, new_mode):
        self.current_mode = new_mode
        self.refresh_all_views()

    def on_data_changed(self):
        self.refresh_all_views()

    def refresh_all_views(self):
        self.update_global_total_label()
        
        for marker in self.markers_widgets:
            marker.refresh_text(self.current_mode)
            self.update_marker_position(marker)

        if self.props_panel.current_data:
            self.props_panel.update_info(self.props_panel.current_data)

    def create_overlays(self):
        for data in self.markers_data:
            marker = OverlayMarker(data, self.on_marker_clicked)
            proxy = self.scene.addWidget(marker)
            marker.scene_proxy = proxy
            marker.refresh_text(self.current_mode)
            self.update_marker_position(marker)
            self.markers_widgets.append(marker)

    def update_marker_position(self, marker):
        cx, cy = marker.data['position']
        w = marker.width()
        h = marker.height()
        if hasattr(marker, 'scene_proxy'):
            marker.scene_proxy.setPos(cx - w / 2, cy - h / 2)

    def on_marker_clicked(self, data):
        self.props_panel.update_info(data)

    def show_error(self, message):
        lbl = QLabel(message, self)
        lbl.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(lbl)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    IMAGE_PATH = Path.cwd() / "tools/misc/nudge2/states_view.png"
    
    target_data = []
    
    try:
        states = get_all_states() 
        for st in states:
            if st.owner != "MIR": 
                continue
            
            col = get_color_from_seed(str(st.state_id))
            
            target_data.append({
                "state": st,
                "color": col
            })
            
    except Exception as e:
        print(f"Error initializing data: {e}")

    window = MainWindow(IMAGE_PATH, target_data)
    window.show()
    
    sys.exit(app.exec())