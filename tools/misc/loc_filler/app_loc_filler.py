import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QTreeWidget, QTreeWidgetItem, QHeaderView, 
                               QPushButton, QHBoxLayout, QDialog, QTextEdit)
from PySide6.QtCore import Qt

from openrouter_api import query_openrouter
from locfile import LocFile

import json
import re

# Keep your imports
try:
    from loc_collection import LocCollection
except ImportError:
    # UPDATED MOCK: Now supports .get() to test the "Empty" logic
    class LocCollection:
        def __init__(self, path):
            print(f"LocCollection initialized at: {path}")
        def contains(self, key):
            return True # Mock: everything exists
        def get(self, key):
            # Mock: make keys ending in "_desc" empty to test the feature
            if key.endswith("_desc"):
                return "   " 
            return "Localisation Text"

from pdx_parser import *

# --- 1. SETUP PATHS ---
BASE_PATH = Path(__file__).parent.parent.parent.parent.resolve()

VANILLA_PATH = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\localisation\english')

# --- 2. CUSTOM EXTRACTION FUNCTIONS ---
# (Keeping these exactly as they were in your original file)
def get_names_focuses(file_path: Path):
    fobj = ParseListFromFile_asPObj(file_path)
    ret = []
    if fobj.Has("focus_tree"):
        focuses = fobj.Get("focus_tree").GetAll("focus").value
        for focus in focuses:
            ret.append(focus.Get("id").value)
            ret.append(focus.Get("id").value + "_desc")
    elif fobj.Has("shared_focus"):
        focuses = fobj.GetAll("shared_focus").value
        for focus in focuses:
            ret.append(focus.Get("id").value)
            ret.append(focus.Get("id").value + "_desc")
    elif fobj.Has("joint_focus"):
        focuses = fobj.GetAll("joint_focus").value
        for focus in focuses:
            ret.append(focus.Get("id").value)
            ret.append(focus.Get("id").value + "_desc")
    return ret

def get_names_decisions(file_path: Path):
    fobj = ParseListFromFile_asPObj(file_path)
    ret = []
    for cat in fobj.value:
        ret.append(cat.id)
        for dec in cat.value:
            ret.append(dec.id)
            ret.append(dec.id + "_desc")
    return ret

def get_names_raids(file_path: Path):
    fobj = ParseListFromFile_asPObj(file_path)
    ret = []
    if fobj.HasNot("types"):
        return ret
    for raids in fobj.Get("types").value:
        ret.append("raid_type_" + raids.id)
        ret.append("raid_type_" + raids.id + "_desc")
    return ret

def get_names_ideas(file_path: Path):
    fobj = ParseListFromFile_asPObj(file_path)
    ret = []
    if fobj.HasNot("ideas"):
        return ret
    iobj = fobj.Get("ideas")
    for cat in iobj.value:
        for idea in cat.value:
            if idea.ValueIsList() and idea.HasNot("name") and cat.HasNot("designer"):
                ret.append(idea.id)
                if cat.id == "country":
                    ret.append(idea.id + "_desc")
    return ret

def get_names_dynmodifiers(file_path: Path):
    fobj = ParseListFromFile_asPObj(file_path)
    ret = []
    for mod in fobj.value:
        ret.append(mod.id)
        if mod.Has("icon"):
            ret.append(mod.id + "_desc")
    return ret

def get_names_country_leader(file_path: Path):
    fobj = ParseListFromFile_asPObj(file_path)
    ret = []
    if fobj.HasNot("leader_traits"):
        return ret
    for trait in fobj.Get("leader_traits").value:
        ret.append(trait.id)
    return ret

def get_names_technologies(file_path: Path):
    fobj = ParseListFromFile_asPObj(file_path)
    ret = []
    if fobj.HasNot("technologies"):
        return ret
    for tech in fobj.Get("technologies").value:
        if tech.Has("enable_equipments"):
            for equip in tech.Get("enable_equipments").value:
                ret.append(equip.id)
                ret.append(equip.id + "_desc")
        elif tech.Has("enable_equipment_modules"):
            for equip in tech.Get("enable_equipment_modules").value:
                ret.append(equip.id)
                ret.append(equip.id + "_desc")
        else:
            ret.append(tech.id)
            if tech.Has("folder"):
                ret.append(tech.id + "_desc")
    return ret

# --- 3. CONFIGURATION ---
DIR_CONFIG = {
    "common/national_focus": get_names_focuses,
    "common/decisions": get_names_decisions,
    "common/raids": get_names_raids,
    "common/ideas": get_names_ideas,
    "common/dynamic_modifiers": get_names_dynmodifiers,
    "common/country_leader": get_names_country_leader,
    "common/unit_leader": get_names_country_leader,
    "common/technologies": get_names_technologies,
}


def process_auto_fill(missing_keys):
    # 1. Define Target File
    target_path = BASE_PATH / "localisation" / "english" / "0_lotr_core" / "lotr_temp_l_english.yml"
    locfile = LocFile(target_path)

    # 2. Filter Keys
    # Discard variables (starting with @)
    valid_keys = [k for k in missing_keys if not k.startswith("@")]
    
    # Separate keys that need LLM generation (names) from descriptions
    keys_for_llm = [k for k in valid_keys if not k.endswith("_desc")]

    if not keys_for_llm:
        print("No keys suitable for AI generation found.")
        return

    # 3. Construct Prompt
    # We ask for a JSON object to ensure strict mapping between Key -> Generated Name
    system_instruction = (
        "You are a localisation helper for a Lord of the Rings (LOTR) strategy game mod.\n"
        "Your task is to convert technical IDs into human-readable English names (Book Title Case).\n"
        "Rules:\n"
        "1. Remove technical prefixes (e.g., 'HAR_', 'gob_', 'generic_') and suffixes.\n"
        "2. Remove trailing numbers (e.g., '_2' should be ignored).\n"
        "3. Replace underscores with spaces and capitalize like a book title.\n"
        "4. Use LOTR-specific spelling and accents where appropriate (e.g., 'Barad-dûr', 'Lórien').\n"
        "5. Return the result strictly as a JSON object where keys are the input IDs and values are the generated text.\n"
        "\n"
        "Example Input: ['HAR_expand_military_production', 'plunder_barad_dur']\n"
        "Example Output: {\"HAR_expand_military_production\": \"Expand Military Production\", \"plunder_barad_dur\": \"Plunder Barad-dûr\"}"
    )

    prompt_content = f"{system_instruction}\n\nInput List:\n{json.dumps(keys_for_llm)}"

    # 4. Query LLM
    try:
        print(f"Querying LLM for {len(keys_for_llm)} keys...")
        response = query_openrouter(prompt_content)
        
        # 5. Parse Response
        # Clean up potential markdown formatting from the LLM
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response.split("```json")[1]
        if clean_response.startswith("```"): # generic code block
            clean_response = clean_response.split("```")[1]
        if clean_response.endswith("```"):
            clean_response = clean_response.split("```")[0]
        
        generated_map = json.loads(clean_response)

    except Exception as e:
        print(f"Error querying or parsing LLM response: {e}")
        generated_map = {}

    # 6. Apply to LocFile
    # We iterate over 'valid_keys' to maintain the exact order requested
    count_added = 0
    for key in valid_keys:
        if key.endswith("_desc"):
            locfile.add(key, "TODO")
        else:
            # Retrieve from LLM map, fallback to basic formatting if LLM failed for that specific key
            if key in generated_map:
                locfile.add(key, generated_map[key])
            else:
                # Fallback: simple replace and title case
                fallback_val = key.replace("_", " ").title()
                locfile.add(key, fallback_val)
        count_added += 1

    # 7. Save
    locfile.save(target_path)
    print(f"Successfully saved {count_added} keys to {target_path.name}")



# --- 5. HELPER UI CLASSES ---
class TextDialog(QDialog):
    """A simple dialog to display text, optionally with an Auto-Fill button."""
    def __init__(self, title, text, parent=None, on_autofill=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        self.text_area = QTextEdit()
        self.text_area.setPlainText(text)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)
        
        # Button Layout
        btn_layout = QHBoxLayout()
        
        # Close Button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        # NEW: Auto-Fill Button
        if on_autofill:
            fill_btn = QPushButton("Auto-Fill")
            # Style it nicely (Blue)
            fill_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
            fill_btn.clicked.connect(on_autofill)
            fill_btn.clicked.connect(self.accept) # Close dialog after triggering
            btn_layout.addWidget(fill_btn)
            
        layout.addLayout(btn_layout)


# --- 6. UI IMPLEMENTATION ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Localisation Key Checker")
        self.resize(1100, 600) 

        # Setup Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Directory / File", "Status", "Defined", "Empty", "Missing", "Actions"])
        
        # Column Resizing
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tree)

        # Initial Load
        self.refresh_data()

    def refresh_data(self):
        """Reloads the collection and repopulates the tree."""
        # 1. Re-initialize the collection to read latest files from disk
        loc_path = str(BASE_PATH / "localisation")
        self.collection = LocCollection(loc_path)

        self.collection._scan_directory(VANILLA_PATH)
        
        # 2. Clear visual tree
        self.tree.clear()
        
        # 3. Populate
        self.populate_tree()

    def populate_tree(self):
        for relative_dir, extractor_func in DIR_CONFIG.items():
            full_dir_path = BASE_PATH / relative_dir
            
            # Create Directory Item
            dir_item = QTreeWidgetItem(self.tree)
            dir_item.setText(0, relative_dir)
            
            if not full_dir_path.exists():
                dir_item.setText(1, "Not Found")
                dir_item.setForeground(1, Qt.GlobalColor.red)
                continue
            
            dir_item.setText(1, "Scanning...")

            total_defined = 0
            total_empty = 0
            total_missing = 0

            try:
                files = sorted(list(full_dir_path.glob("*.txt")))
                
                for file_path in files:
                    file_item = QTreeWidgetItem(dir_item)
                    file_item.setText(0, file_path.name)
                    
                    # 1. Extract Keys
                    keys = extractor_func(file_path)
                    
                    # 2. Analyze Keys
                    defined_count = 0
                    empty_keys = []
                    missing_keys = []
                    
                    for key in keys:
                        if self.collection.contains(key):
                            val = self.collection.get(key)
                            if val and len(str(val).strip()) > 0:
                                defined_count += 1
                            else:
                                empty_keys.append(key)
                        else:
                            missing_keys.append(key)
                    
                    empty_count = len(empty_keys)
                    missing_count = len(missing_keys)
                    
                    # 3. Update Text Data
                    file_item.setText(2, str(defined_count))
                    file_item.setText(3, str(empty_count))
                    file_item.setText(4, str(missing_count))
                    file_item.setText(1, "Done")
                    
                    # Color coding logic
                    if missing_count > 0:
                        file_item.setForeground(4, Qt.GlobalColor.red)
                    elif empty_count > 0:
                        file_item.setForeground(3, Qt.GlobalColor.darkYellow)
                    else:
                        file_item.setForeground(1, Qt.GlobalColor.darkGreen)

                    # 4. Add Buttons
                    self.add_action_buttons(file_item, missing_keys, empty_keys)

                    total_defined += defined_count
                    total_empty += empty_count
                    total_missing += missing_count

                # Update Directory Totals
                dir_item.setText(1, f"{len(files)} files")
                dir_item.setText(2, str(total_defined))
                dir_item.setText(3, str(total_empty))
                dir_item.setText(4, str(total_missing))
                
                # Expand if there are issues
                if total_missing > 0 or total_empty > 0:
                    dir_item.setExpanded(True)
                else:
                    dir_item.setExpanded(False)

            except Exception as e:
                dir_item.setText(1, f"Error: {str(e)}")

    def add_action_buttons(self, item, missing_keys, empty_keys):
        """Creates a widget with buttons based on what is needed."""
        if not missing_keys and not empty_keys:
            return

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(5)

        # Button: Show Missing
        if missing_keys:
            btn_miss = QPushButton(f"Missing ({len(missing_keys)})")
            btn_miss.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_miss.setStyleSheet("color: red;")
            
            # UPDATED: Pass the execute_autofill method to the dialog
            btn_miss.clicked.connect(lambda ch=False, k=missing_keys: self.show_list_dialog(
                "Missing Keys", k, enable_autofill=True
            ))
            layout.addWidget(btn_miss)

        # Button: Show Empty
        if empty_keys:
            btn_empty = QPushButton(f"Empty ({len(empty_keys)})")
            btn_empty.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_empty.setStyleSheet("color: #D4AC0D;") 
            # Note: No autofill for "Empty" keys, as per request
            btn_empty.clicked.connect(lambda ch=False, k=empty_keys: self.show_list_dialog(
                "Empty Keys", k, enable_autofill=False
            ))
            layout.addWidget(btn_empty)

        # Assign widget to the Actions column (index 5)
        self.tree.setItemWidget(item, 5, widget)

    def show_list_dialog(self, title, keys, enable_autofill=False):
        """Displays simple list of keys."""
        content = "\n".join(keys)
        
        # Prepare the callback wrapper
        autofill_callback = None
        if enable_autofill:
            autofill_callback = lambda: self.execute_autofill(keys)

        dialog = TextDialog(title, content, self, on_autofill=autofill_callback)
        dialog.exec()

    def execute_autofill(self, keys):
        """Executes the external logic and then refreshes the UI."""
        # 1. Run the custom logic (defined at top of file)
        process_auto_fill(keys)
        
        # 2. Refresh the whole application to see changes
        self.refresh_data()

    def generate_todo_text(self, keys):
        """Generates the localisation script format."""
        lines = []
        for key in keys:
            lines.append(f' {key}:0 "TODO"')
        
        content = "\n".join(lines)
        dialog = TextDialog("Generated TODOs", content, self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())