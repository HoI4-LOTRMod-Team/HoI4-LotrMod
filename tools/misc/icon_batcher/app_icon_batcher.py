import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
    QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QHeaderView, 
    QLabel, QFileDialog, QFrame, QDialog, QComboBox, QFormLayout,
    QLineEdit
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt

# Importing your external API
from gem_batch_api import *

class JobStartDialog(QDialog):
    """A popup form to configure and create a new job."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Batch Job")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 1. Job Name Input
        self.name_input = QLineEdit()
        self.name_input.setText("my-batch-job")
        self.name_input.setPlaceholderText("Enter a unique job name...")
        form_layout.addRow("Job Name:", self.name_input)

        # 2. Model Selection Dropdown
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", 
            "gemini-2.5-flash-preview", "gemini-3-pro-preview", 
            "gemini-2.5-flash-image", "gemini-3-pro-image-preview"
        ])
        form_layout.addRow("Model ID:", self.model_combo)

        # 3. File Selection
        self.file_path_label = QLabel("No JSON file selected")
        self.file_path_label.setStyleSheet("color: gray; font-style: italic;")
        self.json_path = None
        
        btn_browse = QPushButton("Browse JSON...")
        btn_browse.clicked.connect(self.browse_file)
        form_layout.addRow("Input Data:", btn_browse)
        form_layout.addRow("", self.file_path_label)

        layout.addLayout(form_layout)

        # 4. Action Buttons
        button_box = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_submit = QPushButton("Create Job")
        self.btn_submit.setEnabled(False) # Wait for file selection
        self.btn_submit.setStyleSheet("background-color: #1976d2; color: white; font-weight: bold;")
        self.btn_submit.clicked.connect(self.accept)
        
        button_box.addStretch()
        button_box.addWidget(btn_cancel)
        button_box.addWidget(self.btn_submit)
        layout.addLayout(button_box)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if file_path:
            self.json_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            self.file_path_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
            self.btn_submit.setEnabled(True)

    def get_data(self):
        """Returns (filepath, model_id, job_name)"""
        return self.json_path, self.model_combo.currentText(), self.name_input.text()


class JobManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini Batch Manager")
        self.resize(1200, 850)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- JOBS SECTION HEADER ---
        job_header_layout = QHBoxLayout()
        job_header_layout.addWidget(QLabel("<h2>Job Monitor</h2>"))
        job_header_layout.addStretch()
        
        btn_start_job = QPushButton("▶ Create New Job")
        btn_start_job.setStyleSheet("background-color: #1976d2; color: white; font-weight: bold; padding: 6px 20px;")
        btn_start_job.clicked.connect(self.handle_create_job_dialog)
        job_header_layout.addWidget(btn_start_job)
        self.main_layout.addLayout(job_header_layout)

        # --- JOBS TABLE ---
        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(5)
        self.jobs_table.setHorizontalHeaderLabels(["Name", "Display Name", "State", "Created At", "Actions"])
        self.jobs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.jobs_table)

        # Visual Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

        # --- FILES SECTION HEADER ---
        file_header_layout = QHBoxLayout()
        file_header_layout.addWidget(QLabel("<h2>Stored Files</h2>"))
        file_header_layout.addStretch()
        
        btn_upload = QPushButton("+ Upload New File")
        btn_upload.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 6px 20px;")
        btn_upload.clicked.connect(self.handle_upload)
        file_header_layout.addWidget(btn_upload)
        self.main_layout.addLayout(file_header_layout)

        # --- FILES TABLE ---
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(5)
        self.files_table.setHorizontalHeaderLabels(["Name", "Display Name", "MIME Type", "URI", "Actions"])
        self.files_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.files_table)

        # Initial data fetch
        self.load_jobs()
        self.load_files()

    # --- HANDLERS ---
    def handle_create_job_dialog(self):
        dialog = JobStartDialog(self)
        if dialog.exec():
            json_path, model_id, job_name = dialog.get_data()
            
            # Use the new create_job function
            create_job(json_path, model_id, job_name)
            
            # Refresh both lists as the job creation might involve file movements/generation
            self.load_jobs()
            self.load_files()

    def handle_update_job(self, row, job):
        updated_job = update_job_status(job)
        self.refresh_job_row(row, updated_job)

    def handle_cancel_job(self, row, job):
        cancel_job(job)
        self.handle_update_job(row, job)

    def handle_delete_job(self, job):
        delete_job(job)
        self.load_jobs()

    def handle_copy_uri(self, uri_text):
        QGuiApplication.clipboard().setText(uri_text)

    def handle_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if file_path:
            upload_file(file_path, os.path.basename(file_path))
            self.load_files()

    def handle_delete_file(self, file):
        delete_file(file)
        self.load_files()

    # --- REFRESH LOGIC ---
    def load_jobs(self):
        jobs = get_jobs_list()
        self.jobs_table.setRowCount(len(jobs))
        for row, job in enumerate(jobs):
            self.refresh_job_row(row, job)

    def refresh_job_row(self, row, job):
        self.jobs_table.setItem(row, 0, QTableWidgetItem(job.name))
        self.jobs_table.setItem(row, 1, QTableWidgetItem(job.display_name))
        self.jobs_table.setItem(row, 2, QTableWidgetItem(job.state.name))
        self.jobs_table.setItem(row, 3, QTableWidgetItem(job.create_time.strftime('%Y-%m-%d %H:%M:%S')))
        self.jobs_table.setCellWidget(row, 4, self._create_job_buttons(row, job))

    def _create_job_buttons(self, row, job):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        
        btn_update = QPushButton("Update")
        btn_update.clicked.connect(lambda: self.handle_update_job(row, job))
        layout.addWidget(btn_update)

        if job.state.name == "JOB_STATE_SUCCEEDED":
            btn_retr = QPushButton("Retrieve")
            btn_retr.clicked.connect(lambda: retrieve(job))
            layout.addWidget(btn_retr)
        else:
            btn_can = QPushButton("Cancel")
            btn_can.clicked.connect(lambda: self.handle_cancel_job(row, job))
            layout.addWidget(btn_can)

        btn_del = QPushButton("Delete")
        btn_del.setStyleSheet("color: #d32f2f;")
        btn_del.clicked.connect(lambda checked=False, j=job: self.handle_delete_job(j))
        layout.addWidget(btn_del)
        return container

    def load_files(self):
        files = get_files_list()
        self.files_table.setRowCount(len(files))
        for row, file in enumerate(files):
            self.files_table.setItem(row, 0, QTableWidgetItem(file.name))
            self.files_table.setItem(row, 1, QTableWidgetItem(file.display_name))
            self.files_table.setItem(row, 2, QTableWidgetItem(file.mime_type))
            self.files_table.setItem(row, 3, QTableWidgetItem(file.uri))
            self.files_table.setCellWidget(row, 4, self._create_file_buttons(file))

    def _create_file_buttons(self, file):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        btn_copy = QPushButton("Copy Uri")
        btn_copy.clicked.connect(lambda checked=False, f=file: self.handle_copy_uri(f.uri))
        btn_del = QPushButton("Delete")
        btn_del.setStyleSheet("color: white; background-color: #d32f2f;")
        btn_del.clicked.connect(lambda checked=False, f=file: self.handle_delete_file(f))
        layout.addWidget(btn_copy)
        layout.addWidget(btn_del)
        return container

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = JobManagerWindow()
    window.show()
    sys.exit(app.exec())