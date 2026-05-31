import sys
import os
import shutil
import time
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                               QScrollArea, QFileDialog, QComboBox, QMessageBox, 
                               QProgressBar, QGroupBox, QCheckBox, QSlider)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QPixmap, QImage

# --- Import Dependencies ---
try:
    from rembg import remove, new_session
except ImportError:
    print("Please install rembg: pip install rembg[gpu] OR pip install rembg")
    sys.exit(1)

# --- Import Cloud API ---
try:
    from remove_bg_api import process_image
    HAS_CLOUD_API = True
except ImportError:
    print("Warning: remove_bg_api.py not found. Cloud processing will be unavailable.")
    HAS_CLOUD_API = False

# --- Configuration ---
THUMB_SIZE = QSize(250, 250)
MODELS = ['u2net', 'isnet-general-use', 'isnet-anime', 'u2net_human_seg', 'Cloud API']
OUTPUT_DIR_NAME = "processed_outputs"

# --- Default Parameters ---
DEFAULT_AM_ENABLED = True
DEFAULT_AM_BG_THRESH = 10
DEFAULT_AM_FG_THRESH = 240
DEFAULT_AM_ERODE = 10

class WorkerThread(QThread):
    """
    Background worker with Pause and Stop capabilities.
    """
    update_signal = Signal(object, bytes) 
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, tasks, model_name, am_params):
        super().__init__()
        self.tasks = tasks 
        self.model_name = model_name
        self.am_params = am_params # Dictionary of alpha matting params
        self.is_running = True
        self.is_paused = False

    def run(self):
        session = None
        
        if self.model_name != 'Cloud API':
            try:
                session = new_session(self.model_name)
            except Exception as e:
                self.error_signal.emit(f"Failed to load model: {e}")
                return
        elif self.model_name == 'Cloud API' and not HAS_CLOUD_API:
            self.error_signal.emit("Cloud API script (remove_bg_api.py) is missing!")
            return

        for file_path in self.tasks:
            if not self.is_running: break
            
            while self.is_paused:
                self.msleep(100)
                if not self.is_running: return

            try:
                with open(file_path, 'rb') as i:
                    input_data = i.read()
                
                if self.model_name == 'Cloud API':
                    output_data = process_image(input_data, use_preview=True)
                else:
                    # Pass dynamic parameters here
                    output_data = remove(
                        input_data,
                        session=session,
                        alpha_matting=self.am_params['enabled'],
                        alpha_matting_background_threshold=self.am_params['bg_thresh'],
                        alpha_matting_foreground_threshold=self.am_params['fg_thresh'],
                        alpha_matting_erode_size=self.am_params['erode']
                    )

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
    Row Widget with Process (Blue), Save (Green), Discard (Red), and Keep Original (Cyan).
    """
    save_clicked = Signal(QWidget)          
    discard_clicked = Signal(QWidget)       
    save_original_clicked = Signal(QWidget)
    process_clicked = Signal(QWidget)       

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
        self.frame_processed, self.lbl_proc_img, self.btn_process, self.btn_save, self.btn_discard = self.create_processed_frame()

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
            btn_keep = QPushButton("Keep Original")
            btn_keep.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
            btn_keep.clicked.connect(lambda: self.save_original_clicked.emit(self))
            v_layout.addWidget(btn_keep)
        else:
            v_layout.addStretch() 

        return container

    def create_processed_frame(self):
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(0,0,0,0)

        lbl_img = QLabel("Waiting...")
        lbl_img.setFixedSize(THUMB_SIZE)
        lbl_img.setAlignment(Qt.AlignCenter)
        lbl_img.setStyleSheet("background-color: #222; border: 1px dashed #666; color: #888;")

        btn_layout = QHBoxLayout()

        # Process Button
        btn_process = QPushButton("Process")
        btn_process.setStyleSheet("background-color: #3F51B5; color: white; padding: 5px; font-weight: bold;")
        btn_process.clicked.connect(lambda: self.process_clicked.emit(self))

        btn_save = QPushButton("Save")
        btn_save.setEnabled(False) 
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px; font-weight: bold;")
        btn_save.clicked.connect(lambda: self.save_clicked.emit(self))

        btn_discard = QPushButton("Discard")
        btn_discard.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        btn_discard.clicked.connect(lambda: self.discard_clicked.emit(self))

        btn_layout.addWidget(btn_process) 
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_discard)

        v_layout.addWidget(lbl_img)
        v_layout.addLayout(btn_layout)

        return container, lbl_img, btn_process, btn_save, btn_discard

    def update_processed_image(self, image_data):
        self.processed_data = image_data
        
        image = QImage.fromData(image_data)
        pixmap = QPixmap.fromImage(image)
        self.lbl_proc_img.setPixmap(pixmap.scaled(THUMB_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.lbl_proc_img.setStyleSheet("background-color: #333; border: 1px solid #555;")
        
        self.btn_save.setEnabled(True)
        self.btn_process.setEnabled(True) 

    def reset_state(self):
        self.processed_data = None
        self.lbl_proc_img.clear()
        self.lbl_proc_img.setText("Processing...")
        self.lbl_proc_img.setStyleSheet("background-color: #222; border: 1px dashed #666; color: #888;")
        self.btn_save.setEnabled(False)
        self.btn_process.setEnabled(False) 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Batch Background Remover")
        self.resize(1100, 850)
        self.worker = None
        self.row_map = {} 

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)

        self.setup_ui()
        self.setup_alpha_matting_ui() # Initialize the new UI section

    def setup_ui(self):
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

        self.btn_toggle = QPushButton("Start Batch") 
        self.btn_toggle.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_toggle.clicked.connect(self.toggle_batch_processing)
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

    def setup_alpha_matting_ui(self):
        """Creates the controls for Alpha Matting parameters."""
        group = QGroupBox("Alpha Matting Settings")
        group_layout = QHBoxLayout(group)
        group_layout.setContentsMargins(10, 10, 10, 10)

        # 1. Main Checkbox
        self.chk_alpha = QCheckBox("Enable Alpha Matting")
        self.chk_alpha.setChecked(DEFAULT_AM_ENABLED)
        self.chk_alpha.toggled.connect(self.toggle_sliders)

        # 2. Background Threshold Slider (0-50)
        lbl_bg = QLabel("BG Thresh:")
        self.slider_bg = QSlider(Qt.Horizontal)
        self.slider_bg.setRange(0, 50)
        self.slider_bg.setValue(DEFAULT_AM_BG_THRESH)
        self.lbl_bg_val = QLabel(str(DEFAULT_AM_BG_THRESH))
        self.lbl_bg_val.setFixedWidth(25)
        self.slider_bg.valueChanged.connect(lambda v: self.lbl_bg_val.setText(str(v)))

        # 3. Foreground Threshold Slider (220-255)
        lbl_fg = QLabel("FG Thresh:")
        self.slider_fg = QSlider(Qt.Horizontal)
        self.slider_fg.setRange(220, 255) # Range as requested
        self.slider_fg.setValue(DEFAULT_AM_FG_THRESH)
        self.lbl_fg_val = QLabel(str(DEFAULT_AM_FG_THRESH))
        self.lbl_fg_val.setFixedWidth(25)
        self.slider_fg.valueChanged.connect(lambda v: self.lbl_fg_val.setText(str(v)))

        # 4. Erode Size Slider (0-50)
        lbl_erode = QLabel("Erode Size:")
        self.slider_erode = QSlider(Qt.Horizontal)
        self.slider_erode.setRange(0, 50)
        self.slider_erode.setValue(DEFAULT_AM_ERODE)
        self.lbl_erode_val = QLabel(str(DEFAULT_AM_ERODE))
        self.lbl_erode_val.setFixedWidth(25)
        self.slider_erode.valueChanged.connect(lambda v: self.lbl_erode_val.setText(str(v)))

        # 5. Reset Button
        btn_reset = QPushButton("Reset Defaults")
        btn_reset.setFixedWidth(100)
        btn_reset.clicked.connect(self.reset_alpha_params)

        # Add to Layout
        group_layout.addWidget(self.chk_alpha)
        
        # Add a vertical separator line
        line = QWidget()
        line.setFixedWidth(1)
        line.setStyleSheet("background-color: #666;")
        group_layout.addWidget(line)

        group_layout.addWidget(lbl_bg)
        group_layout.addWidget(self.slider_bg)
        group_layout.addWidget(self.lbl_bg_val)
        
        group_layout.addWidget(lbl_fg)
        group_layout.addWidget(self.slider_fg)
        group_layout.addWidget(self.lbl_fg_val)
        
        group_layout.addWidget(lbl_erode)
        group_layout.addWidget(self.slider_erode)
        group_layout.addWidget(self.lbl_erode_val)

        group_layout.addStretch()
        group_layout.addWidget(btn_reset)

        self.main_layout.addWidget(group)

        # Add Progress Bar and Scroll Area (moved here to keep layout order)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid grey; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #4CAF50; width: 20px; }")
        self.main_layout.addWidget(self.progress_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

    def toggle_sliders(self, checked):
        self.slider_bg.setEnabled(checked)
        self.slider_fg.setEnabled(checked)
        self.slider_erode.setEnabled(checked)

    def reset_alpha_params(self):
        self.chk_alpha.setChecked(DEFAULT_AM_ENABLED)
        self.slider_bg.setValue(DEFAULT_AM_BG_THRESH)
        self.slider_fg.setValue(DEFAULT_AM_FG_THRESH)
        self.slider_erode.setValue(DEFAULT_AM_ERODE)

    def get_alpha_params(self):
        return {
            'enabled': self.chk_alpha.isChecked(),
            'bg_thresh': self.slider_bg.value(),
            'fg_thresh': self.slider_fg.value(),
            'erode': self.slider_erode.value()
        }

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.path_input.setText(folder)

    def load_images(self):
        folder_path = self.path_input.text()
        if not folder_path or not os.path.exists(folder_path): return

        self.cancel_processing()
        
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.row_map.clear()

        path_obj = Path(folder_path)
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        
        for file_path in path_obj.iterdir():
            if file_path.suffix.lower() in valid_extensions:
                row = ImageRow(file_path)
                row.save_clicked.connect(self.save_single_row)
                row.discard_clicked.connect(self.discard_row)
                row.save_original_clicked.connect(self.save_original_row)
                row.process_clicked.connect(self.process_single_row)
                
                self.scroll_layout.addWidget(row)
                self.row_map[file_path] = row
        
        if self.row_map:
            self.btn_toggle.setEnabled(True)
            self.btn_save_all.setEnabled(True)
            self.progress_bar.setValue(0)

    # --- Processing Logic ---

    def toggle_batch_processing(self):
        if self.worker is None:
            tasks = []
            for file_path, row in self.row_map.items():
                row.reset_state()
                tasks.append(file_path)
            self.start_processing(tasks)
        
        elif not self.worker.is_paused:
            self.worker.pause()
            self.btn_toggle.setText("Resume Batch")
            self.btn_toggle.setStyleSheet("background-color: #FFC107; color: black; font-weight: bold;")
        
        else:
            self.worker.resume()
            self.btn_toggle.setText("Pause Batch")
            self.btn_toggle.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

    def process_single_row(self, row_widget):
        if self.worker is not None:
            QMessageBox.warning(self, "Busy", "Please wait for current processing to finish or Cancel it.")
            return

        row_widget.reset_state()
        self.start_processing([row_widget.file_path])

    def start_processing(self, tasks):
        if not tasks:
            QMessageBox.information(self, "Info", "No images to process.")
            return

        self.btn_toggle.setText("Pause")
        self.btn_cancel.setEnabled(True)
        self.combo_model.setEnabled(False)
        self.btn_save_all.setEnabled(False)
        self.set_all_process_buttons_enabled(False) 
        
        self.progress_bar.setRange(0, len(tasks))
        self.progress_bar.setValue(0)

        model_name = self.combo_model.currentText()
        
        # Capture current slider values
        params = self.get_alpha_params()
        
        self.worker = WorkerThread(tasks, model_name, params)
        self.worker.update_signal.connect(self.on_worker_update)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.error_signal.connect(self.on_worker_error)
        self.worker.start()

    def set_all_process_buttons_enabled(self, enabled):
        """Helper to lock/unlock all individual process buttons."""
        for row in self.row_map.values():
            row.btn_process.setEnabled(enabled)

    def cancel_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.on_worker_finished()

    def on_worker_update(self, file_path, data):
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        if file_path in self.row_map:
            self.row_map[file_path].update_processed_image(data)

    def on_worker_finished(self):
        self.worker = None
        self.btn_toggle.setText("Start Batch")
        self.btn_toggle.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_cancel.setEnabled(False)
        self.combo_model.setEnabled(True)
        self.btn_save_all.setEnabled(True)
        self.set_all_process_buttons_enabled(True) 

    def on_worker_error(self, err_msg):
        QMessageBox.critical(self, "Error", err_msg)
        self.cancel_processing()

    # --- File Operations ---
    def ensure_output_dir(self, source_path):
        output_dir = source_path.parent / OUTPUT_DIR_NAME
        if not output_dir.exists(): output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def save_single_row(self, row_widget):
        if not row_widget.processed_data: return
        try:
            output_dir = self.ensure_output_dir(row_widget.file_path)
            output_filename = f"{row_widget.file_path.stem}.png"
            output_path = output_dir / output_filename
            with open(output_path, 'wb') as f: f.write(row_widget.processed_data)
            self.discard_row(row_widget)
        except Exception as e: QMessageBox.critical(self, "Save Error", str(e))

    def save_original_row(self, row_widget):
        try:
            output_dir = self.ensure_output_dir(row_widget.file_path)
            shutil.copy2(row_widget.file_path, output_dir / row_widget.file_path.name)
            self.discard_row(row_widget)
        except Exception as e: QMessageBox.critical(self, "Save Error", str(e))

    def discard_row(self, row_widget):
        file_path = row_widget.file_path
        if file_path in self.row_map: del self.row_map[file_path]
        self.scroll_layout.removeWidget(row_widget)
        row_widget.deleteLater()
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