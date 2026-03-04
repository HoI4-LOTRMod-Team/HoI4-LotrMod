import sys
import os
import re
from collections import defaultdict

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTextEdit, QListWidget, QLabel, QMessageBox,
                               QListWidgetItem)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

# --- Assumed Imports ---
from pdx_parser import *
from locfile import LocFile

# --- Hard-Coded Paths ---
MD_PATH = r"C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\retrievals\2026-03-04_11-25-09"
FOCUS_FILE = r"C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\common\national_focus\spiders.txt"
LOC_FILE = r"C:\Users\ben32801\Documents\Paradox Interactive\Hearts of Iron IV\mod\lotr\localisation\english\spiders\spiders_focuses_l_english.yml"

class FocusDescEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HOI4 Focus Description Helper")
        self.resize(900, 600) # Widened the window to fit the side panel comfortably
        
        self.init_data()
        self.init_ui()
        self.load_focus(0)

    def init_data(self):
        self.loc_file = LocFile(LOC_FILE)
        self.focus_list = ParseListFromFile_asPObj(FOCUS_FILE).Get("focus_tree").GetAll("focus").value
        #self.focus_list = ParseListFromFile_asPObj(FOCUS_FILE).GetAll("shared_focus").value
        self.current_index = 0
        self.M = defaultdict(list)
        
        pattern = re.compile(r'^([^:]+):\d*\s+"(.*)"\s*$')
        
        if os.path.exists(MD_PATH):
            for filename in os.listdir(MD_PATH):
                if filename.endswith(".md"):
                    filepath = os.path.join(MD_PATH, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            
                            match = pattern.match(line)
                            if match:
                                focus_id = match.group(1)
                                description = match.group(2)
                                self.M[focus_id].append(description)
        else:
            print(f"Warning: MD_PATH '{MD_PATH}' does not exist.")

    def init_ui(self):
        # --- NEW: Main Horizontal Layout ---
        self.main_layout = QHBoxLayout(self)

        # --- Left Side: Editor ---
        self.left_layout = QVBoxLayout()
        
        self.info_label = QLabel("Loading...")
        self.left_layout.addWidget(self.info_label)

        self.options_list = QListWidget()
        self.options_list.itemClicked.connect(self.on_option_selected)
        self.options_list.setWordWrap(True)
        self.options_list.setSpacing(6)
        self.left_layout.addWidget(self.options_list)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Description will appear here. You can also type a new one manually.")
        self.text_edit.setMaximumHeight(150) 
        self.left_layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        
        self.btn_skip = QPushButton("Skip")
        self.btn_skip.clicked.connect(self.skip)
        btn_layout.addWidget(self.btn_skip)

        self.btn_next = QPushButton("Next (Save)")
        self.btn_next.clicked.connect(self.next_focus)
        self.btn_next.setStyleSheet("background-color: #2b5c8f; color: white; font-weight: bold;") 
        btn_layout.addWidget(self.btn_next)

        self.left_layout.addLayout(btn_layout)

        # --- Right Side: Context Panel ---
        self.right_layout = QVBoxLayout()
        
        self.effect_label = QLabel("<b>Focus Effects (Context):</b>")
        self.right_layout.addWidget(self.effect_label)
        
        self.effect_display = QTextEdit()
        self.effect_display.setReadOnly(True) # Ensure the user doesn't try to edit the code here
        # Give it a slightly different background to distinguish it from the editor
        self.effect_display.setStyleSheet("background-color: #f4f4f4; color: #333333; font-family: Consolas, monospace;") 
        self.right_layout.addWidget(self.effect_display)

        # Add both sides to the main layout, giving the left side slightly more room (stretch 3 vs 2)
        self.main_layout.addLayout(self.left_layout, stretch=3)
        self.main_layout.addLayout(self.right_layout, stretch=2)

    def load_focus(self, index):
        if index >= len(self.focus_list):
            self.info_label.setText("<b>Finished! All focuses have been processed.</b>")
            self.options_list.clear()
            self.text_edit.clear()
            self.effect_display.clear()
            self.btn_next.setEnabled(False)
            self.btn_skip.setEnabled(False)
            QMessageBox.information(self, "Done", "You have reached the end of the focus list.")
            return

        self.current_index = index
        current_focus = self.focus_list[self.current_index]
        
        base_id = current_focus.Get("id").value
        self.target_id = f"{base_id}_desc"

        self.info_label.setText(
            f"<b>Focus ID:</b> {base_id} <br>"
            f"<b>Target Loc ID:</b> {self.target_id} <br>"
            f"<i>Progress: {index + 1} / {len(self.focus_list)}</i>"
        )

        self.options_list.clear()
        self.text_edit.clear()
        
        # --- NEW: Populate the Effects Panel ---
        reward = current_focus.Get("completion_reward")
        if reward:
            self.effect_display.setPlainText("\t" + str(reward))
        else:
            self.effect_display.setPlainText("\tNo completion reward defined for this focus.")
        # ---------------------------------------
        
        item_to_select = None

        if self.loc_file.contains(self.target_id):
            existing_desc = self.loc_file.get(self.target_id)
            item = QListWidgetItem(existing_desc)
            
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            item.setBackground(QColor("#2d2d2d"))
            # --- FIXED: Set text color to white for contrast against dark grey ---
            item.setForeground(QColor("white")) 
            
            item.setToolTip("Currently saved description")
            
            self.options_list.addItem(item)
            item_to_select = item

        descriptions = self.M.get(self.target_id, [])
        if descriptions:
            for desc in descriptions:
                item = QListWidgetItem(desc)
                self.options_list.addItem(item)
                
                if item_to_select is None:
                    item_to_select = item
                    
        elif self.options_list.count() == 0:
            warning_item = QListWidgetItem("--- No pre-written descriptions found ---")
            warning_item.setFlags(warning_item.flags() & ~Qt.ItemIsSelectable)
            self.options_list.addItem(warning_item)

        if item_to_select:
            self.options_list.setCurrentItem(item_to_select)
            self.text_edit.setPlainText(item_to_select.text())

    def on_option_selected(self, item):
        if not item.text().startswith("---"):
            self.text_edit.setPlainText(item.text())

    def skip(self):
        self.load_focus(self.current_index + 1)

    def next_focus(self):
        new_desc = self.text_edit.toPlainText().strip()
        self.loc_file.set(self.target_id, new_desc)
        self.loc_file.save(LOC_FILE)
        self.load_focus(self.current_index + 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FocusDescEditor()
    window.show()
    sys.exit(app.exec())