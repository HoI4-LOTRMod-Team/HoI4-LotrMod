import sys
import os
import time
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                               QScrollArea, QFileDialog, QComboBox, QMessageBox, 
                               QProgressBar)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QPixmap, QImage

# Import rembg dependencies
try:
    from rembg import remove, new_session
except ImportError:
    print("Please install rembg: pip install rembg[gpu] OR pip install rembg")
    sys.exit(1)

# --- Configuration ---
THUMB_SIZE = QSize(250, 250)
MODELS = ['u2net', 'isnet-general-use', 'isnet-anime', 'u2net_human_seg']
OUTPUT_DIR_NAME = "processed_outputs"

class WorkerThread(QThread):
    """
    Background worker with Pause and Stop capabilities.
    """
    update_signal = Signal(object, bytes) 
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, tasks, model_name):
        super().__init__()
        self.tasks = tasks 
        self.model_name = model_name
        self.is_running = True
        self.is_paused = False

    def run(self):
        try:
            session = new_session(self.model_name)
        except Exception as e:
            self.error_signal.emit(f"Failed to load model: {e}")
            return

        for file_path in self.tasks:
            # Check for Stop
            if not self.is_running:
                break
            
            # Check for Pause
            while self.is_paused:
                self.msleep(100) # Sleep 100ms and check again
                if not self.is_running:
                    return

            try:
                with open(file_path, 'rb') as i:
                    input_data = i.read()
                
                output_data = remove(input_data, session=session)
                self.update_signal.emit(file_path, output_data)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        self.finished_signal.emit()

    def stop(self):
        self.is_running = False

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

class ImageRow(QWidget):
    """
    Row Widget with Save (Green) and Discard (Red) buttons.
    """
    save_clicked = Signal(QWidget)    # Signal to save
    discard_clicked = Signal(QWidget) # Signal to remove without saving

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.processed_data = None 
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Left Side (Original)
        self.frame_original = self.create_visual_frame(self.file_path, is_original=True)
        
        # Right Side (Processed + Buttons)
        self.frame_processed, self.lbl_proc_img, self.btn_save, self.btn_discard = self.create_processed_frame()

        layout.addWidget(self.frame_original)
        layout.addWidget(self.frame_processed)
        
        self.setStyleSheet("ImageRow { border-bottom: 1px solid #444; }")

    def create_visual_frame(self, image_source, is_original=False):
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(0,0,0,0)
        
        lbl_img = QLabel()
        lbl_img.setFixedSize(THUMB_SIZE)
        lbl_img.setAlignment(Qt.AlignCenter)
        lbl_img.setStyleSheet("background-color: #333; border: 1px solid #555;")
        
        pixmap = QPixmap(str(image_source))
        if not pixmap.isNull():
            lbl_img.setPixmap(pixmap.scaled(THUMB_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        lbl_txt = QLabel(image_source.name)
        lbl_txt.setAlignment(Qt.AlignCenter)
        lbl_txt.setWordWrap(True)

        v_layout.addWidget(lbl_img)
        v_layout.addWidget(lbl_txt)
        
        if is_original:
            v_layout.addStretch() 

        return container

    def create_processed_frame(self):
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(0,0,0,0)

        # Image Placeholder
        lbl_img = QLabel("Waiting...")
        lbl_img.setFixedSize(THUMB_SIZE)
        lbl_img.setAlignment(Qt.AlignCenter)
        lbl_img.setStyleSheet("background-color: #222; border: 1px dashed #666; color: #888;")

        # Buttons Layout
        btn_layout = QHBoxLayout()

        # Save Button
        btn_save = QPushButton("Save")
        btn_save.setEnabled(False) 
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px; font-weight: bold;")
        btn_save.clicked.connect(lambda: self.save_clicked.emit(self))

        # Discard Button
        btn_discard = QPushButton("Discard")
        btn_discard.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        btn_discard.clicked.connect(lambda: self.discard_clicked.emit(self))

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_discard)

        v_layout.addWidget(lbl_img)
        v_layout.addLayout(btn_layout)

        return container, lbl_img, btn_save, btn_discard

    def update_processed_image(self, image_data):
        self.processed_data = image_data
        
        image = QImage.fromData(image_data)
        pixmap = QPixmap.fromImage(image)
        self.lbl_proc_img.setPixmap(pixmap.scaled(THUMB_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.lbl_proc_img.setStyleSheet("background-color: #333; border: 1px solid #555;")
        
        self.btn_save.setEnabled(True)

    def reset_state(self):
        self.processed_data = None
        self.lbl_proc_img.clear()
        self.lbl_proc_img.setText("Processing...")
        self.lbl_proc_img.setStyleSheet("background-color: #222; border: 1px dashed #666; color: #888;")
        self.btn_save.setEnabled(False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Batch Background Remover")
        self.resize(1100, 800)
        self.worker = None
        self.row_map = {} 

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)

        self.setup_ui()

    def setup_ui(self):
        # --- Top Control Bar ---
        top_bar = QHBoxLayout()
        
        self.path_input = QLineEdit(os.getcwd())
        btn_browse = QPushButton("...")
        btn_browse.setFixedWidth(30)
        btn_browse.clicked.connect(self.browse_folder)

        btn_load = QPushButton("Load Images")
        btn_load.clicked.connect(self.load_images)

        self.combo_model = QComboBox()
        self.combo_model.addItems(MODELS)
        self.combo_model.setCurrentText('isnet-general-use')

        # Control Buttons
        self.btn_toggle = QPushButton("Start Processing") # Dual purpose: Start/Pause
        self.btn_toggle.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_toggle.clicked.connect(self.toggle_processing)
        self.btn_toggle.setEnabled(False)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("background-color: #607D8B; color: white;")
        self.btn_cancel.clicked.connect(self.cancel_processing)
        self.btn_cancel.setEnabled(False)

        self.btn_save_all = QPushButton("Save All")
        self.btn_save_all.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        self.btn_save_all.clicked.connect(self.save_all)
        self.btn_save_all.setEnabled(False)

        top_bar.addWidget(self.path_input)
        top_bar.addWidget(btn_browse)
        top_bar.addWidget(btn_load)
        top_bar.addWidget(QLabel("Model:"))
        top_bar.addWidget(self.combo_model)
        top_bar.addWidget(self.btn_toggle)
        top_bar.addWidget(self.btn_cancel)
        top_bar.addWidget(self.btn_save_all)
        
        self.main_layout.addLayout(top_bar)

        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid grey; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #4CAF50; width: 20px; }")
        self.main_layout.addWidget(self.progress_bar)

        # --- Scroll Area ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.path_input.setText(folder)

    def load_images(self):
        folder_path = self.path_input.text()
        if not folder_path or not os.path.exists(folder_path):
            return

        self.cancel_processing() # Reset everything
        
        # Clear UI
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.row_map.clear()

        # Load files
        path_obj = Path(folder_path)
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        
        for file_path in path_obj.iterdir():
            if file_path.suffix.lower() in valid_extensions:
                row = ImageRow(file_path)
                # Connect signals
                row.save_clicked.connect(self.save_single_row)
                row.discard_clicked.connect(self.discard_row)
                
                self.scroll_layout.addWidget(row)
                self.row_map[file_path] = row
        
        if self.row_map:
            self.btn_toggle.setEnabled(True)
            self.btn_save_all.setEnabled(True)
            self.progress_bar.setValue(0)

    def toggle_processing(self):
        # Case 1: Not running -> Start
        if self.worker is None:
            self.start_new_batch()
        
        # Case 2: Running -> Pause
        elif not self.worker.is_paused:
            self.worker.pause()
            self.btn_toggle.setText("Resume")
            self.btn_toggle.setStyleSheet("background-color: #FFC107; color: black; font-weight: bold;")
        
        # Case 3: Paused -> Resume
        else:
            self.worker.resume()
            self.btn_toggle.setText("Pause")
            self.btn_toggle.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

    def start_new_batch(self):
        # 1. Identify pending tasks (processed_data is None)
        tasks = []
        for file_path, row in self.row_map.items():
            if row.processed_data is None:
                row.reset_state()
                tasks.append(file_path)

        if not tasks:
            QMessageBox.information(self, "Info", "All loaded images are already processed.")
            return

        # 2. Setup UI for processing
        self.btn_toggle.setText("Pause")
        self.btn_cancel.setEnabled(True)
        self.combo_model.setEnabled(False)
        self.btn_save_all.setEnabled(False)
        
        # Progress Bar logic:
        # We want the bar to represent the whole list, so we set range to total images
        # and value to (total - pending).
        total_images = len(self.row_map)
        done_images = total_images - len(tasks)
        self.progress_bar.setRange(0, total_images)
        self.progress_bar.setValue(done_images)

        # 3. Start Thread
        model_name = self.combo_model.currentText()
        self.worker = WorkerThread(tasks, model_name)
        self.worker.update_signal.connect(self.on_worker_update)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.error_signal.connect(self.on_worker_error)
        self.worker.start()

    def cancel_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait() # Wait for it to safely exit
        
        self.on_worker_finished() # Reset UI state

    def on_worker_update(self, file_path, data):
        # Update progress bar
        self.progress_bar.setValue(self.progress_bar.value() + 1)

        # Update Row (check if it still exists!)
        if file_path in self.row_map:
            self.row_map[file_path].update_processed_image(data)

    def on_worker_finished(self):
        self.worker = None
        self.btn_toggle.setText("Start Processing")
        self.btn_toggle.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_cancel.setEnabled(False)
        self.combo_model.setEnabled(True)
        self.btn_save_all.setEnabled(True)

    def on_worker_error(self, err_msg):
        QMessageBox.critical(self, "Error", err_msg)
        self.cancel_processing()

    # --- File Operations ---

    def ensure_output_dir(self, source_path):
        output_dir = source_path.parent / OUTPUT_DIR_NAME
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def save_single_row(self, row_widget):
        if not row_widget.processed_data: return

        try:
            output_dir = self.ensure_output_dir(row_widget.file_path)
            output_filename = f"{row_widget.file_path.stem}.png"
            output_path = output_dir / output_filename
            
            with open(output_path, 'wb') as f:
                f.write(row_widget.processed_data)
            
            self.discard_row(row_widget) # Save successful, so remove
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def discard_row(self, row_widget):
        """Removes the row from UI and memory."""
        file_path = row_widget.file_path
        
        if file_path in self.row_map:
            del self.row_map[file_path]
        
        self.scroll_layout.removeWidget(row_widget)
        row_widget.deleteLater()

        # Update progress bar total if removing a row during operation is weird, 
        # but usually we just leave the bar as is until restart.
        
        if not self.row_map:
            self.btn_toggle.setEnabled(False)
            self.btn_save_all.setEnabled(False)

    def save_all(self):
        rows_to_process = list(self.row_map.values())
        saved_count = 0
        for row in rows_to_process:
            if row.processed_data:
                self.save_single_row(row)
                saved_count += 1
        
        if saved_count == 0:
            QMessageBox.information(self, "Info", "No processed images found to save.")

    def closeEvent(self, event):
        self.cancel_processing()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())