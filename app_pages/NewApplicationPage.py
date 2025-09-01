import json
import os
import sqlite3

from PyQt5.QtWidgets import QLineEdit, QTextEdit, QWidget, QTabWidget, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QMessageBox, QProgressBar
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from AI_queries.generate_cv import generate_cv
from AI_queries.summarise_job import summarise_job
from AI_queries.generate_cover_letter import generate_cover_letter
from file_generation.generate_docx import generate_docx

from database.Database import Database

class NewApplicationPage(QWidget):
    def __init__(self, db: Database, tabs: QTabWidget):
        super().__init__()
        self.tabs = tabs
        self.db_path = "database/applications_database.db"
        self.job_data = {}
        self.setWindowTitle("New Application Page")
        self.init_ui()

    def init_ui(self):
        # Set layout style to vertical
        self.layout = QVBoxLayout()

        # Single line job title textbox
        self.job_title_textbox = QLineEdit()
        self.job_title_textbox.setPlaceholderText("Add job title here")
        self.layout.addWidget(self.job_title_textbox)

        # Single line job company textbox
        self.job_company_textbox = QLineEdit()
        self.job_company_textbox.setPlaceholderText("Add job company here")
        self.layout.addWidget(self.job_company_textbox)

        # Single line job deadline textbox
        self.job_deadline_textbox = QLineEdit()
        self.job_deadline_textbox.setPlaceholderText("Add submission deadline here. Type 'rolling' if no deadline")
        self.layout.addWidget(self.job_deadline_textbox)

        # Multi-line job description textbox
        self.job_desc_textbox = QTextEdit()
        self.job_desc_textbox.setPlaceholderText("Add job description here")
        self.layout.addWidget(self.job_desc_textbox, stretch=2)

        # Checkboxes
        self.checkbox_layout = QHBoxLayout()
        self.CV_checkbox = QCheckBox("CV")
        self.cover_letter_checkbox = QCheckBox("Cover Letter")
        self.CV_checkbox.setChecked(True)
        self.cover_letter_checkbox.setChecked(False)
        # self.cover_letter_checkbox.setDisabled(True)
        self.checkbox_layout.addWidget(self.CV_checkbox)
        self.checkbox_layout.addWidget(self.cover_letter_checkbox)
        self.layout.addLayout(self.checkbox_layout, stretch=1)

        # Buttons
        self.button_layout = QHBoxLayout()

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.process_submission)
        self.button_layout.addWidget(self.submit_button, stretch=1)

        # Clear Button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_all)
        self.button_layout.addWidget(self.clear_button, stretch=1)

        self.layout.addLayout(self.button_layout, stretch=1)

        # Status box
        self.status_box = QLineEdit()
        self.status_box.setReadOnly(True)
        self.layout.addWidget(self.status_box)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)   # 0% to 100%
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)

    def process_submission(self):
        # Check that at least one of the CV/CL checkboxes is ticked
        if (not self.CV_checkbox.isChecked()) and (not self.cover_letter_checkbox.isChecked()):
            QMessageBox.warning(self, "Invalid Entry", "CV and/or Cover Letter needs to be checked")
            return
        
        # Clear status box and set progress bar to zero
        self.status_box.clear()
        self.progress_bar.setValue(0)

        # Read in data from the form
        self.job_data["title"] = self.job_title_textbox.text()
        self.job_data["company"] = self.job_company_textbox.text()
        self.job_data["deadline"] = self.job_deadline_textbox.text()
        self.job_data["description"] = self.job_desc_textbox.toPlainText()
        self.job_data["status"] = "Draft"
        self.job_data["version"] = 1
        self.job_data["CV_checkbox"] = self.CV_checkbox.isChecked()
        self.job_data["cover_letter_checkbox"] = self.cover_letter_checkbox.isChecked()
        
        # Create a new thread
        self.thread = QThread()
        self.worker = SubmitWorker(self.job_data, self.db_path, self.tabs)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status_update.connect(self.update_status)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def update_status(self, message):
        self.status_box.setText(message)

    def clear_all(self):
        self.job_title_textbox.clear()
        self.job_company_textbox.clear()
        self.job_deadline_textbox.clear()
        self.job_desc_textbox.clear()

class SubmitWorker(QObject):
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, job_data, db_path, tabs):
        super().__init__()
        self.job_data = job_data
        self.db_path = db_path
        self.tabs = tabs

    def run(self):
        self.db = Database(self.db_path)

        # Get the AI job summary
        self.status_update.emit("Analysing job description...")
        self.progress.emit(10)
        self.job_summary = summarise_job(self.job_data["description"]).model_dump()
        
        # Merge the manually entered job data and the AI-inferred information
        self.job_summary = {k: v for k, v in self.job_data.items() if k in ["title", "company", "deadline", "description"]} | self.job_summary

        # Open the Master CV file (will add file uploader to form later)
        with open('inputs/master_cv.json', 'r', encoding="utf-8") as f:
            self.master_cv = json.dumps(json.load(f))

        self.progress.emit(50)

        # Insert the new entry into the database, and get back the entry id (for file saving purposes)
        self.job_id = self.db.new_entry(self.job_data["company"], self.job_data["title"], self.job_data["deadline"], self.job_data["status"])

        # Write the job description json file to correct location
        with open(self.get_file_path("JobDescription", "json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(self.job_summary, indent=2))

        # Perform if CV checkbox ticked
        if self.job_data["CV_checkbox"]:
            # Get the new AI CV
            self.status_update.emit("Tailoring CV...")
            self.new_CV = generate_cv(json.dumps(self.job_summary, indent=2), self.master_cv)

            self.file_path_CV_json = self.get_file_path("CV", "json")
            self.file_path_CV_docx = self.get_file_path("CV", "docx")

            # Write the new CV json file to correct location
            with open(self.file_path_CV_json, "w", encoding="utf-8") as f:
                f.write(self.new_CV.model_dump_json())

            # Generate word document template
            generate_docx(self.file_path_CV_docx, "templates/cv_template.docx", self.file_path_CV_json)

            # Update the database to include the link to the docx file (for button functionality)
            self.db.add_file_path(self.job_id, self.file_path_CV_docx)

        # Perform if CL checkbox ticked
        if self.job_data["cover_letter_checkbox"]:
            # Get the new AI CL
            self.status_update.emit("Generating Cover Letter...")
            self.progress.emit(75)
            self.new_cover_letter = generate_cover_letter(self.job_summary, self.master_cv)

            self.file_path_CL_json = self.get_file_path("CL", "json")
            self.file_path_CL_docx = self.get_file_path("CL", "docx")

            # Write the new CL json file to correct location
            with open(self.file_path_CL_json, "w", encoding="utf-8") as f:
                f.write(self.new_cover_letter.model_dump_json())

            # Generate word document template
            generate_docx(self.file_path_CL_docx, "templates/CL_template.docx", self.file_path_CL_json)

        self.status_update.emit("Saving...")
        self.progress.emit(90)

        # Save the files. Will allow different formats later
        # self.save_files()

        # Update the database to include the link to the docx file (for button functionality)
        # self.db.add_file_path(self.job_id, self.file_path_CV_docx)

        self.status_update.emit("Done!")
        self.progress.emit(100)
        self.finished.emit()

        self.tabs.setCurrentIndex(1)

    def get_file_path(self, file, file_type):
        # Create application folders
        folder_path = rf"C:\Users\maxca\Desktop\tailor_my_CV\applications\{self.job_id}_{self.job_data['title']}_{self.job_data['company']}\{file_type}"
        os.makedirs(folder_path, exist_ok=True)

        file_path = rf"{folder_path}\{file}_{self.job_data['title']}_{self.job_id}_V{self.job_data['version']}.{file_type}"

        return file_path


    # Save the files. Will allow different formats later
    def save_files_old(self):
        # Create application folders
        self.folder_path_json = rf"C:\Users\maxca\Desktop\tailor_my_CV\applications\{self.job_id}_{self.job_data['title']}_{self.job_data['company']}\json"
        self.folder_path_docx = rf"C:\Users\maxca\Desktop\tailor_my_CV\applications\{self.job_id}_{self.job_data['title']}_{self.job_data['company']}\docx"

        os.makedirs(self.folder_path_json, exist_ok=True)
        os.makedirs(self.folder_path_docx, exist_ok=True)

        self.file_path_JobDescription_json = rf"{self.folder_path_json}\JobDescription_{self.job_data['title']}_{self.job_id}_V{self.job_data['version']}.json"

        self.file_path_CV_json = rf"{self.folder_path_json}\CV_{self.job_data['title']}_{self.job_id}_V{self.job_data['version']}.json"
        self.file_path_CV_docx = rf"{self.folder_path_docx}\CV_{self.job_data['title']}_{self.job_id}_V{self.job_data['version']}.docx"

        self.file_path_CL_json = rf"{self.folder_path_json}\CL_{self.job_data['title']}_{self.job_id}_V{self.job_data['version']}.json"
        self.file_path_CL_docx = rf"{self.folder_path_docx}\CL_{self.job_data['title']}_{self.job_id}_V{self.job_data['version']}.docx"

        # Write the job description json file to correct location
        with open(self.file_path_JobDescription_json, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.job_summary, indent=2))

        # Write the new CV json file to correct location
        with open(self.file_path_CV_json, "w", encoding="utf-8") as f:
            f.write(self.new_CV.model_dump_json())

        # Generate word document template
        generate_docx(self.file_path_CV_docx, "templates/cv_template.docx", self.file_path_CV_json)
