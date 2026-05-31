import sys
import numpy as np
from PIL import Image
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout, 
    QVBoxLayout, QFrame, QPushButton, QSpinBox, QComboBox,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QStackedWidget,
    QGridLayout, QGraphicsItem
)
from PySide6.QtGui import QPixmap, QColor, QFont, QPainter, QTransform, QAction, QKeySequence
from PySide6.QtCore import Qt
from pathlib import Path

# --- RESTORED IMPORTS ---
from definitioncsv import * # --- CONSTANTS ---
MODE_MANPOWER = "Manpower"
MODE_INFRASTRUCTURE = "Infrastructure"
MODE_ARMS = "Arms Factory"
MODE_INDUSTRY = "Industrial Complex"
MODE_CATEGORY = "State Category"
MODE_RESOURCES = "Resources"
MODE_PROSPECTIVE = "Prospective Resources"

CATEGORIES = [
    "wasteland", "enclave", "tiny_island", "pastoral", "rural", 
    "town", "large_town", "city", "large_city", "metropolis", "megalopolis"
]

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

        def get_val(obj, default=0):
            try: return int(obj.value)
            except: return default

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
                                val = int(float(res_obj.Get(r_type).value))
                            except:
                                val = 0
                        res_dict[r_type] = val
                        res_total += val
                except:
                    for r_type in RESOURCE_TYPES: res_dict[r_type] = 0

                # 5. Prospective Resources (NEW)
                prosp_dict = {}
                prosp_total = 0
                try:
                    history = state_obj.pObj.Get("history")
                    if history:
                        for r_type in RESOURCE_TYPES:
                            dep_val = 0
                            var_name = f"{r_type}_deposit"
                            # Using user logic to check existence
                            vars_found = history.GetAll("set_variable").WithField(var_name)
                            if len(vars_found.value) > 0:
                                try:
                                    # Using user logic to get value
                                    dep_val = int(vars_found.value[0].Get(var_name).value)
                                except:
                                    dep_val = 0
                            
                            prosp_dict[r_type] = dep_val
                            prosp_total += dep_val
                except Exception as e:
                    print(f"Error parsing prospective: {e}")
                    for r_type in RESOURCE_TYPES: prosp_dict[r_type] = 0

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
                    "prospective_resources": prosp_dict, # <--- NEW DATA
                    "prospective_total": prosp_total,    # <--- NEW DATA
                    
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
        val_str = "?"
        show_share = True

        if mode == MODE_CATEGORY:
            val_str = self.data.get('state_category', 'rural')
            self.setText(val_str)
            self.adjustSize()
            return
        
        elif mode == MODE_RESOURCES or mode == MODE_PROSPECTIVE:
            parts = []
            # Determine which dict to look at
            dict_key = 'resources' if mode == MODE_RESOURCES else 'prospective_resources'
            res_data = self.data.get(dict_key, {})
            
            for r_type in RESOURCE_TYPES:
                val = res_data.get(r_type, 0)
                if val > 0:
                    short = RESOURCE_SHORTS.get(r_type, r_type[:3])
                    parts.append(f"{val}{short}")
            
            if not parts: val_str = "-"
            else:
                val_str = ", ".join(parts)
                # Add prefix for prospective to distinguish visually
                if mode == MODE_PROSPECTIVE:
                    val_str = "Dep: " + val_str
                
                if len(val_str) > 15:
                    val_str = val_str.replace(", ", "\n")
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
    def __init__(self, parent_callback):
        super().__init__()
        self.parent_callback = parent_callback
        self.spinboxes = {}
        
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for idx, r_type in enumerate(RESOURCE_TYPES):
            lbl = QLabel(r_type.title() + ":")
            lbl.setFont(QFont("Arial", 9))
            # FIX: Ensure label text is dark
            lbl.setStyleSheet("color: #333333;")
            
            sb = QSpinBox()
            sb.setRange(0, 9999)
            sb.setSingleStep(1)
            sb.setProperty("resource_type", r_type)
            # FIX: Ensure spinbox background is white and text is black
            sb.setStyleSheet("QSpinBox { color: #000000; background-color: #ffffff; }")
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
    def __init__(self, on_value_change_callback, on_mode_change_callback, on_save_callback):
        super().__init__()
        self.on_value_change = on_value_change_callback
        self.on_mode_change = on_mode_change_callback
        self.on_save = on_save_callback
        
        self.current_data = None
        self.is_updating_ui = False 
        self.current_mode = MODE_MANPOWER

        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedWidth(250)
        
        # --- FIX: Main styling for the panel to enforce light theme look ---
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-left: 1px solid #ccc;
                color: #000000; /* Default text color for the frame */
            }
            QLabel {
                color: #000000;
            }
            QComboBox {
                color: #000000;
                background-color: #ffffff;
                selection-background-color: #0078d7;
                selection-color: #ffffff;
            }
            QSpinBox {
                color: #000000;
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        
        lbl_mode = QLabel("Editing Mode:")
        lbl_mode.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(lbl_mode)
        
        self.combo_mode = QComboBox()
        self.combo_mode.addItems([
            MODE_MANPOWER, MODE_INFRASTRUCTURE, MODE_ARMS,
            MODE_INDUSTRY, MODE_CATEGORY, MODE_RESOURCES, MODE_PROSPECTIVE
        ])
        self.combo_mode.currentTextChanged.connect(self.on_mode_changed_internal)
        layout.addWidget(self.combo_mode)
        
        layout.addSpacing(10)
        
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

        self.input_stack = QStackedWidget()
        self.spin_value = QSpinBox()
        self.spin_value.valueChanged.connect(self.on_spinbox_changed)
        self.input_stack.addWidget(self.spin_value)
        
        self.combo_category = QComboBox()
        self.combo_category.addItems(CATEGORIES)
        self.combo_category.currentTextChanged.connect(self.on_category_changed)
        self.input_stack.addWidget(self.combo_category)

        self.res_editor = ResourceEditorWidget(self.on_resource_changed)
        self.input_stack.addWidget(self.res_editor)
        
        layout.addWidget(self.input_stack)
        
        # Spacer to push save button to bottom
        layout.addStretch()
        
        # --- SAVE BUTTON ---
        self.btn_save = QPushButton("Save Changes")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_save.clicked.connect(self.on_save)
        layout.addWidget(self.btn_save)

        self.update_ui_mode_state()

    def update_ui_mode_state(self):
        self.spin_value.blockSignals(True)
        
        if self.current_mode == MODE_CATEGORY:
            self.input_stack.setCurrentWidget(self.combo_category)
            self.lbl_total_global.setVisible(False)
            self.lbl_share_stats.setVisible(False)
        elif self.current_mode == MODE_RESOURCES or self.current_mode == MODE_PROSPECTIVE:
            self.input_stack.setCurrentWidget(self.res_editor)
            self.lbl_total_global.setVisible(True) 
            self.lbl_share_stats.setVisible(False) 
        else:
            self.input_stack.setCurrentWidget(self.spin_value)
            self.lbl_total_global.setVisible(True)
            self.lbl_share_stats.setVisible(True)

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
        self.lbl_total_global.setWordWrap(True)
        
        if self.current_mode == MODE_CATEGORY: 
            return 
            
        if (self.current_mode == MODE_RESOURCES or self.current_mode == MODE_PROSPECTIVE) and isinstance(total_val, dict):
            parts = []
            for r_type in RESOURCE_TYPES:
                val = total_val.get(r_type, 0)
                if val > 0:
                    short_name = RESOURCE_SHORTS.get(r_type, r_type[:3]).title()
                    val_str = format_k(val)
                    parts.append(f"{short_name}: {val_str}")
            
            label_prefix = "Total Res" if self.current_mode == MODE_RESOURCES else "Total Dep"
            if not parts:
                self.lbl_total_global.setText(f"{label_prefix}: 0")
            else:
                self.lbl_total_global.setText(f"{label_prefix}: " + ", ".join(parts))
        else:
            formatted = format_k(total_val) if self.current_mode == MODE_MANPOWER else str(total_val)
            label_txt = f"Total {self.current_mode}:"
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
        
        if self.current_mode == MODE_CATEGORY:
            current_cat = data.get('state_category', 'rural')
            idx = self.combo_category.findText(current_cat)
            self.combo_category.setCurrentIndex(max(0, idx))
            
        elif self.current_mode == MODE_RESOURCES:
            self.res_editor.load_values(data.get('resources', {}))
        
        elif self.current_mode == MODE_PROSPECTIVE:
            self.res_editor.load_values(data.get('prospective_resources', {}))
            
        else:
            key_map = {
                MODE_MANPOWER: 'manpower', MODE_INFRASTRUCTURE: 'infrastructure',
                MODE_ARMS: 'arms_factory', MODE_INDUSTRY: 'industrial_complex'
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
                if st.pObj.Get("history").Get("buildings").Has("arms_factory"):
                    st.pObj.Get("history").Get("buildings").Get("arms_factory").value = str(value)
                else:
                    st.pObj.Get("history").Get("buildings").Insert(f"\n\t\t\tarms_factory = {value}")
            elif self.current_mode == MODE_INDUSTRY:
                self.current_data['industrial_complex'] = value
                if st.pObj.Get("history").Get("buildings").Has("industrial_complex"):
                    st.pObj.Get("history").Get("buildings").Get("industrial_complex").value = str(value)
                else:
                    st.pObj.Get("history").Get("buildings").Insert(f"\n\t\t\tindustrial_complex = {value}")
                
            self.on_value_change()
        except Exception as e: print(f"Update failed: {e}")

    def on_category_changed(self, value_text):
        if self.is_updating_ui or self.current_data is None: return
        try:
            self.current_data['state_category'] = value_text
            self.current_data['state'].pObj.Get("state_category").value = value_text
            self.on_value_change()
        except Exception as e: print(f"Category update failed: {e}")

    def on_resource_changed(self, r_type, value):
        if self.is_updating_ui or self.current_data is None: return
        
        st_obj = self.current_data['state']
        
        try:
            if self.current_mode == MODE_RESOURCES:
                # --- STANDARD RESOURCES LOGIC ---
                res_obj = st_obj.pObj.Get("resources") 
                if res_obj is None:
                    res_obj = st_obj.pObj.Insert("\n\tresources = { }").Get("resources")
                
                self.current_data['resources'][r_type] = value
                
                if value > 0:
                    if res_obj.Has(r_type): res_obj.Get(r_type).value = str(value)
                    else: res_obj.Insert(f"\n\t\t{r_type} = {value}")
                else:
                    if res_obj.Has(r_type): res_obj.Remove(r_type)
                
                self.current_data['resources_total'] = sum(self.current_data['resources'].values())
            
            elif self.current_mode == MODE_PROSPECTIVE:
                # --- PROSPECTIVE RESOURCES LOGIC (NEW) ---
                var_name = f"{r_type}_deposit"
                history = st_obj.pObj.Get("history")
                
                # Check for existing variables using the user's syntax
                existing_vars = history.GetAll("set_variable").WithField(var_name)
                
                self.current_data['prospective_resources'][r_type] = value
                
                if value > 0:
                    if len(existing_vars.value) > 0:
                        # UPDATE: st.pObj.Get("history").GetAll("set_variable").WithField("oil_deposit").value[0].value = 5
                        existing_vars.value[0].Get(var_name).value = str(value)
                    else:
                        # INSERT: st.pObj.Get("history").Insert(f"\n\t\tset_variable = { oil_deposit = 5 }")
                        history.Insert(f"\n\t\tset_variable = {{ {var_name} = {value} }}")
                        print(f"Inserted new prospective resource variable: {var_name} = {value}")
                else:
                    # DELETE: If value is 0, we should remove it.
                    # Since we don't have a specific remove syntax from the user, 
                    # we attempt to find the specific item and remove it from history if possible.
                    if len(existing_vars.value) > 0:
                        history.RemoveAllWhere(lambda item: item.id == "set_variable" and item.Has(var_name))

                self.current_data['prospective_total'] = sum(self.current_data['prospective_resources'].values())

            self.on_value_change()
        except Exception as e: print(f"Resource/Prospective update failed: {e}")

class MainWindow(QMainWindow):
    def __init__(self, image_path, target_data):
        super().__init__()
        self.setWindowTitle("State Distribution Tool")
        self.resize(1100, 750)
        self.current_mode = MODE_MANPOWER
        
        # Store original target_data so we can save even those not visible on map
        self.original_target_data = target_data
        self.markers_widgets = [] 
        
        pil_img, self.markers_data = ImageAnalyzer.analyze_states(image_path, target_data)
        
        self.recalculate_stats()

        if pil_img is None:
            self.show_error(f"Could not load image: {image_path}")
            return

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
            on_mode_change_callback=self.on_mode_changed,
            on_save_callback=self.save_changes
        )
        
        main_layout.addWidget(self.view, 1)
        main_layout.addWidget(self.props_panel)
        
        self.create_overlays()
        self.update_global_total_label()

        # Add Status Bar for save confirmation
        self.statusBar = self.statusBar()
        
        # Setup shortcut (Ctrl+S)
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_action.triggered.connect(self.save_changes)
        self.addAction(self.save_action)

    def save_changes(self):
        """Iterates through all target states and calls save_to_file."""
        count = 0
        try:
            for item in self.original_target_data:
                st = item['state']
                st.save_to_file()
                count += 1
            
            self.statusBar.showMessage(f"Successfully saved {count} states to file.", 5000)
            print(f"Saved {count} states.")
        except Exception as e:
            self.statusBar.showMessage(f"Error saving files: {str(e)}", 5000)
            print(f"Save error: {e}")

    def recalculate_stats(self):
        if self.current_mode == MODE_CATEGORY: return 0 
        
        if self.current_mode == MODE_RESOURCES or self.current_mode == MODE_PROSPECTIVE:
            # --- NEW LOGIC: Sum each resource type individually ---
            totals = {r: 0 for r in RESOURCE_TYPES}
            dict_key = 'resources' if self.current_mode == MODE_RESOURCES else 'prospective_resources'
            
            for item in self.markers_data:
                res_dict = item.get(dict_key, {})
                for r in RESOURCE_TYPES:
                    totals[r] += res_dict.get(r, 0)
            return totals 
            
        else:
            # --- EXISTING LOGIC FOR OTHER MODES ---
            key_map = {
                MODE_MANPOWER: 'manpower', MODE_INFRASTRUCTURE: 'infrastructure',
                MODE_ARMS: 'arms_factory', MODE_INDUSTRY: 'industrial_complex'
            }
            key = key_map.get(self.current_mode)
            
            total = sum(item[key] for item in self.markers_data)
        
            # Update percentage shares (only relevant for single-value modes)
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
            
            proxy.setFlag(QGraphicsItem.ItemIgnoresTransformations)
            proxy.setZValue(10) 
            
            marker.scene_proxy = proxy
            marker.refresh_text(self.current_mode)
            self.update_marker_position(marker)
            self.markers_widgets.append(marker)

    def update_marker_position(self, marker):
        cx, cy = marker.data['position']
        w = marker.width()
        h = marker.height()
        if hasattr(marker, 'scene_proxy'):
            # 1. Set the anchor point in the scene
            marker.scene_proxy.setPos(cx, cy)
            # 2. Apply a local translation to center the widget on that anchor point
            marker.scene_proxy.setTransform(QTransform().translate(-w/2, -h/2))

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
            if st.owner != "GLD" and st.owner != "RGL" and st.owner != "VAL": continue
            col = get_color_from_seed(str(st.state_id))
            target_data.append({ "state": st, "color": col })
    except Exception as e: print(f"Error initializing data: {e}")

    window = MainWindow(IMAGE_PATH, target_data)
    window.show()
    sys.exit(app.exec())