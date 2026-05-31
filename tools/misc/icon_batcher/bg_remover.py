import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                               QScrollArea, QFileDialog, QComboBox, QMessageBox)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QObject
from PySide6.QtGui import QPixmap, QImage

# Import rembg dependencies
try:
    from rembg import remove, new_session
    from PIL import Image
    import io
except ImportError:
    print("Please install necessary libraries: pip install rembg pillow onnxruntime")
    sys.exit(1)

# Configuration
THUMB_SIZE = QSize(250, 250)
MODELS = ['u2net', 'isnet-general-use', 'isnet-anime', 'u2net_human_seg']

class WorkerThread(QThread):
    """
    Runs the background removal task in a separate thread to keep the UI responsive.
    """
    # Signals to communicate back to the Main Window
    update_signal = Signal(int, bytes) # Row Index, Output Data (bytes)
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, tasks, model_name):
        super().__init__()
        self.tasks = tasks # List of tuples: (index, file_path)
        self.model_name = model_name
        self.is_running = True

    def run(self):
        try:
            # Initialize session once per batch for performance
            session = new_session(self.model_name)
        except Exception as e:
            self.error_signal.emit(f"Failed to load model: {e}")
            return

        for index, file_path in self.tasks:
            if not self.is_running:
                break
            
            try:
                with open(file_path, 'rb') as i:
                    input_data = i.read()
                    
                # The heavy lifting
                output_data = remove(input_data, session=session)
                
                # Send result back to GUI
                self.update_signal.emit(index, output_data)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                # We could emit an error signal here, or just skip

        self.finished_signal.emit()

    def stop(self):
        self.is_running = False


class ImageRow(QWidget):
    """
    Represents one image row: Left (Original), Right (Processed)
    """
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.processed_data = None # Store the raw bytes of the result
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(main_layout)

        # Style for the image container (Dark Background)
        # Using a QFrame to hold the label allows us to set a background easily
        self.left_frame = self.create_image_frame(self.file_path)
        self.right_frame = self.create_image_frame(None)

        # Add to main layout
        main_layout.addWidget(self.left_frame)
        main_layout.addWidget(self.right_frame)
        
        # Bottom separator
        self.setStyleSheet("ImageRow { border-bottom: 1px solid #ddd; }")

    def create_image_frame(self, image_source):
        """Helper to create the vertical layout (Image on top, Text on bottom)"""
        frame = QWidget()
        v_layout = QVBoxLayout(frame)
        v_layout.setContentsMargins(0,0,0,0)
        
        # Image Label
        lbl_img = QLabel()
        lbl_img.setFixedSize(THUMB_SIZE)
        lbl_img.setAlignment(Qt.AlignCenter)
        # Dark Grey Background for checking transparency
        lbl_img.setStyleSheet("background-color: #333333; border: 1px solid #555;")
        
        if image_source:
            pixmap = QPixmap(str(image_source))
            if not pixmap.isNull():
                lbl_img.setPixmap(pixmap.scaled(THUMB_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            txt = image_source.name
        else:
            lbl_img.setText("Waiting...")
            lbl_img.setStyleSheet("background-color: #eee; border: 1px dashed #999; color: #999")
            txt = "Processed Output"

        # Text Label
        lbl_txt = QLabel(txt)
        lbl_txt.setAlignment(Qt.AlignCenter)
        lbl_txt.setWordWrap(True)
        lbl_txt.setFixedHeight(20) # Limit height

        v_layout.addWidget(lbl_img)
        v_layout.addWidget(lbl_txt)
        
        # Save reference to image label so we can update it later
        if image_source is None:
            self.lbl_processed_img = lbl_img

        return frame

    def update_processed_image(self, image_data):
        self.processed_data = image_data
        
        # Convert bytes to QImage/QPixmap
        image = QImage.fromData(image_data)
        pixmap = QPixmap.fromImage(image)
        
        # Update Right Label styles to match Left Label (Dark mode)
        self.lbl_processed_img.setStyleSheet("background-color: #333333; border: 1px solid #555;")
        self.lbl_processed_img.setPixmap(pixmap.scaled(THUMB_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Background Remover Tool")
        self.resize(900, 700)
        self.image_rows = [] # Keep track of row widgets
        self.worker = None

        # Main container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)

        # --- Top Bar ---
        top_bar = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(os.getcwd())
        self.path_input.setText(os.getcwd())
        
        btn_browse = QPushButton("...")
        btn_browse.setFixedWidth(30)
        btn_browse.clicked.connect(self.browse_folder)

        btn_load = QPushButton("Load Images")
        btn_load.clicked.connect(self.load_images)

        # Model Selector
        self.combo_model = QComboBox()
        self.combo_model.addItems(MODELS)
        self.combo_model.setCurrentText('isnet-general-use') # Default

        # Action Buttons
        self.btn_start = QPushButton("Start Processing")
        self.btn_start.clicked.connect(self.start_processing)
        self.btn_start.setEnabled(False) # Disabled until images loaded
        self.btn_start.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_processing)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("background-color: #f44336; color: white;")

        top_bar.addWidget(self.path_input)
        top_bar.addWidget(btn_browse)
        top_bar.addWidget(btn_load)
        top_bar.addWidget(QLabel("Model:"))
        top_bar.addWidget(self.combo_model)
        top_bar.addWidget(self.btn_start)
        top_bar.addWidget(self.btn_stop)
        
        self.main_layout.addLayout(top_bar)

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

        # Clear existing
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.image_rows.clear()

        path_obj = Path(folder_path)
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

        for file_path in path_obj.iterdir():
            if file_path.suffix.lower() in valid_extensions:
                row = ImageRow(file_path)
                self.scroll_layout.addWidget(row)
                self.image_rows.append(row)
        
        if self.image_rows:
            self.btn_start.setEnabled(True)

    def start_processing(self):
        if not self.image_rows:
            return

        # 1. Identify which rows need processing
        # (For now, we simply re-process everything, or we could check if row.processed_data is None)
        tasks = []
        for i, row in enumerate(self.image_rows):
            # Optional: Skip already processed ones to act as a "Resume"
            if row.processed_data is None: 
                tasks.append((i, row.file_path))

        if not tasks:
            QMessageBox.information(self, "Info", "All images already processed.")
            return

        # 2. UI State
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.combo_model.setEnabled(False)

        # 3. Start Thread
        model_name = self.combo_model.currentText()
        self.worker = WorkerThread(tasks, model_name)
        self.worker.update_signal.connect(self.on_worker_update)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.error_signal.connect(self.on_worker_error)
        self.worker.start()

    def stop_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.btn_stop.setText("Stopping...") # Visual feedback

    def on_worker_update(self, index, data):
        # Update the specific row
        row = self.image_rows[index]
        row.update_processed_image(data)

    def on_worker_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setText("Stop")
        self.combo_model.setEnabled(True)
        self.worker = None

    def on_worker_error(self, err_msg):
        QMessageBox.critical(self, "Error", err_msg)
        self.on_worker_finished()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())