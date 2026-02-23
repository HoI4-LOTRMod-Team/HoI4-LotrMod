import sys
import os
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QRadioButton, QButtonGroup,
    QMessageBox, QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt

class Occurrence:
    def __init__(self, filepath, line_index, key, value):
        self.filepath = filepath
        self.line_index = line_index  # 0-based index
        self.key = key
        self.value = value
        self.deleted = False

class LocManager:
    def __init__(self):
        self.files_content = {}  # filepath: [line1, line2, ...]
        self.occurrences = {}    # key: [Occurrence, ...]
        self.pattern = re.compile(r'^(\s*)([\w\.\-]+):(\d*)\s*"(.*)"')

    def load_directory(self, root_directory):
        self.files_content.clear()
        self.occurrences.clear()
        
        for root, _, files in os.walk(root_directory):
            for file in files:
                if file.endswith('.yml'):
                    full_path = os.path.join(root, file)
                    self._process_file(full_path)

    def _process_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            self.files_content[filepath] = lines
            
            for idx, line in enumerate(lines):
                match = self.pattern.match(line)
                if match:
                    key = match.group(2)
                    value = match.group(4)
                    occ = Occurrence(filepath, idx, key, value)
                    
                    if key not in self.occurrences:
                        self.occurrences[key] = []
                    self.occurrences[key].append(occ)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    def auto_clean(self):
        """Removes duplicate occurrences that have the same value in the SAME file."""
        cleaned_count = 0
        for key, occs in self.occurrences.items():
            active_occs = [o for o in occs if not o.deleted]
            if len(active_occs) > 1:
                seen = set()
                for o in active_occs:
                    identifier = (o.filepath, o.value)
                    if identifier in seen:
                        o.deleted = True
                        cleaned_count += 1
                    else:
                        seen.add(identifier)
        return cleaned_count

    def get_collisions(self):
        """Returns a list of keys that currently have more than 1 active occurrence."""
        return [k for k, v in self.occurrences.items() if sum(1 for o in v if not o.deleted) > 1]

    def get_active_occurrences(self, key):
        return [o for o in self.occurrences.get(key, []) if not o.deleted]

    def resolve_collision(self, key, keep_occurrence):
        """Marks all occurrences of a key as deleted EXCEPT the chosen one."""
        for o in self.occurrences[key]:
            if o is not keep_occurrence and not o.deleted:
                o.deleted = True

    def save_changes(self):
        """Applies deletions and overwrites the files."""
        # Nullify lines in our memory representation
        for occs in self.occurrences.values():
            for o in occs:
                if o.deleted:
                    self.files_content[o.filepath][o.line_index] = None
        
        # Write back to disk
        files_saved = 0
        for filepath, lines in self.files_content.items():
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line is not None:
                            f.write(line)
                files_saved += 1
            except Exception as e:
                print(f"Error saving {filepath}: {e}")
        return files_saved


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loc Collision Manager")
        self.resize(800, 600)
        self.manager = LocManager()
        
        self.current_key = None
        self.button_to_occurrence = {}
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Controls ---
        top_layout = QHBoxLayout()
        self.btn_load = QPushButton("1. Load Folder")
        self.btn_load.clicked.connect(self.load_folder)
        
        self.btn_clean = QPushButton("2. Auto-Clean (Same File, Same Value)")
        self.btn_clean.clicked.connect(self.auto_clean)
        self.btn_clean.setEnabled(False)
        
        self.btn_save = QPushButton("Save Changes to Disk")
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_save.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_save.setEnabled(False)

        top_layout.addWidget(self.btn_load)
        top_layout.addWidget(self.btn_clean)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_save)
        main_layout.addLayout(top_layout)

        # --- Main Split Content ---
        split_layout = QHBoxLayout()
        
        # Left Panel: Collision List
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>Collisions:</b>"))
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self.on_key_selected)
        left_layout.addWidget(self.list_widget)
        split_layout.addLayout(left_layout, 1)

        # Right Panel: Resolution Details
        right_layout = QVBoxLayout()
        self.lbl_details_title = QLabel("<b>Select a key to view details</b>")
        self.lbl_details_title.setWordWrap(True)
        right_layout.addWidget(self.lbl_details_title)

        # Scroll area for radio buttons
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.radio_container = QWidget()
        self.radio_layout = QVBoxLayout(self.radio_container)
        self.radio_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.radio_container)
        right_layout.addWidget(self.scroll_area)

        self.btn_group = QButtonGroup(self)
        
        self.btn_resolve = QPushButton("Resolve Selection")
        self.btn_resolve.clicked.connect(self.resolve_current)
        self.btn_resolve.setEnabled(False)
        right_layout.addWidget(self.btn_resolve)

        split_layout.addLayout(right_layout, 2)
        main_layout.addLayout(split_layout)

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Root Directory")
        if folder:
            self.manager.load_directory(folder)
            self.btn_clean.setEnabled(True)
            self.btn_save.setEnabled(True)
            self.refresh_list()
            QMessageBox.information(self, "Loaded", f"Scanned folder.\nFound {len(self.manager.occurrences)} unique keys.")

    def auto_clean(self):
        count = self.manager.auto_clean()
        self.refresh_list()
        QMessageBox.information(self, "Auto-Clean", f"Cleaned up {count} exact duplicates in the same files.")

    def refresh_list(self):
        self.list_widget.clear()
        collisions = self.manager.get_collisions()
        self.list_widget.addItems(collisions)
        self.clear_details()

    def clear_details(self):
        self.lbl_details_title.setText("<b>Select a key to view details</b>")
        self.btn_resolve.setEnabled(False)
        self.current_key = None
        
        # Remove old radio buttons
        while self.radio_layout.count():
            item = self.radio_layout.takeAt(0)
            widget = item.widget()
            if widget:
                self.btn_group.removeButton(widget)
                widget.deleteLater()
        self.button_to_occurrence.clear()

    def on_key_selected(self, current, previous):
        self.clear_details()
        if not current:
            return

        self.current_key = current.text()
        active_occs = self.manager.get_active_occurrences(self.current_key)
        
        # Check if values are identical across the different files
        unique_values = set(o.value for o in active_occs)
        if len(unique_values) == 1:
            title = f"<b>Key:</b> {self.current_key}<br><span style='color: blue;'>Status: Identical values across multiple files. Choose which file to keep.</span>"
        else:
            title = f"<b>Key:</b> {self.current_key}<br><span style='color: red;'>Status: Different values found. Choose the correct version.</span>"
            
        self.lbl_details_title.setText(title)

        # Generate Radio Buttons
        for i, occ in enumerate(active_occs):
            filename = os.path.basename(occ.filepath)
            rb_text = f"File: {filename} (Line {occ.line_index + 1})\nValue: \"{occ.value}\""
            rb = QRadioButton(rb_text)
            
            self.btn_group.addButton(rb, i)
            self.radio_layout.addWidget(rb)
            self.button_to_occurrence[i] = occ

        # Enable resolve button when a radio button is clicked
        self.btn_group.buttonClicked.connect(lambda: self.btn_resolve.setEnabled(True))

    def resolve_current(self):
        selected_id = self.btn_group.checkedId()
        if selected_id == -1 or not self.current_key:
            return

        keep_occ = self.button_to_occurrence[selected_id]
        self.manager.resolve_collision(self.current_key, keep_occ)
        
        # Remove from list and select the next one
        current_row = self.list_widget.currentRow()
        self.list_widget.takeItem(current_row)
        
        if self.list_widget.count() > 0:
            next_row = current_row if current_row < self.list_widget.count() else current_row - 1
            self.list_widget.setCurrentRow(next_row)
        else:
            self.clear_details()
            QMessageBox.information(self, "All Done", "All collisions have been resolved! Don't forget to Save Changes.")

    def save_changes(self):
        reply = QMessageBox.question(self, 'Save Changes', 
                                     'This will modify your .yml files. Are you sure?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            saved_count = self.manager.save_changes()
            QMessageBox.information(self, "Saved", f"Successfully updated {saved_count} files.")
            self.refresh_list() # Re-parse basically, or just clear out since they are saved.

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())