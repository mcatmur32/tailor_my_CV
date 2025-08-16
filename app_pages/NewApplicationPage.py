import json
import os

from PyQt5.QtWidgets import QLineEdit, QTextEdit, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QMessageBox

from AI_queries.generate_cv import generate_cv
from AI_queries.summarise_job import summarise_job
from AI_queries.generate_cover_letter import generate_cover_letter
from file_generation.generate_docx import generate_docx

from database.Database import Database

class NewApplicationPage(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("New Application Page")

        # Set layout style to vertical
        main_layout = QVBoxLayout()

        # Single line job title textbox
        self.job_title_textbox = QLineEdit()
        self.job_title_textbox.setPlaceholderText("Add job title here")
        main_layout.addWidget(self.job_title_textbox)

        # Single line job company textbox
        self.job_company_textbox = QLineEdit()
        self.job_company_textbox.setPlaceholderText("Add job company here")
        main_layout.addWidget(self.job_company_textbox)

        # Single line job deadline textbox
        self.job_deadline_textbox = QLineEdit()
        self.job_deadline_textbox.setPlaceholderText("Add submission deadline here. Type 'rolling' if no deadline")
        main_layout.addWidget(self.job_deadline_textbox)

        # Multi-line job description textbox
        self.job_desc_textbox = QTextEdit()
        self.job_desc_textbox.setPlaceholderText("Add job description here")
        main_layout.addWidget(self.job_desc_textbox, stretch=2)

        # Checkboxes
        checkbox_layout = QHBoxLayout()
        self.CV_checkbox = QCheckBox("CV")
        self.cover_letter_checkbox = QCheckBox("Cover Letter")
        self.CV_checkbox.setChecked(True)
        self.cover_letter_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.CV_checkbox)
        checkbox_layout.addWidget(self.cover_letter_checkbox)
        main_layout.addLayout(checkbox_layout, stretch=1)

        # Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.process_submission)
        main_layout.addWidget(self.submit_button, stretch=1)

        self.setLayout(main_layout)

    def process_submission(self):
        # Check that at least one of the CV/CL checkboxes is ticked
        if (not self.CV_checkbox.isChecked()) and (not self.cover_letter_checkbox.isChecked()):
            QMessageBox.warning(self, "Invalid Entry", "CV and/or Cover Letter needs to be checked")
            return
        
        # Read in data from the form
        self.job_title = self.job_title_textbox.text()
        self.job_company = self.job_company_textbox.text()
        self.job_deadline = self.job_deadline_textbox.text()
        self.job_description = self.job_desc_textbox.toPlainText()

        # Set the initial status and version
        self.status = "Draft"
        self.version = 1
        
        # Get the AI job summary
        self.job_summary = summarise_job(self.job_description)
        print(self.job_summary)
        print("\n")

        # Open the Master CV file (will add file uploader to form later)
        with open('inputs/master_cv.json', 'r', encoding="utf-8") as f:
            self.master_cv = json.dumps(json.load(f))

        # Perform if CV checkbox ticked
        if self.CV_checkbox.isChecked():
            # Get the new AI CV
            self.new_CV = generate_cv(json.dumps(self.job_summary.model_dump(), indent=2), self.master_cv)
            print(self.new_CV)
            print("\n")

        # Perform if CL checkbox ticked
        if self.cover_letter_checkbox.isChecked():
            # Get the new AI CL
            self.new_cover_letter = generate_cover_letter(self.job_summary, self.master_cv)
            print(self.new_cover_letter)
            print("\n")

        # Insert the new entry into the database, and get back the entry id (for file saving purposes)
        self.job_id = self.db.new_entry(self.job_company, self.job_title, self.job_deadline, self.status)

        # Save the files. Will allow different formats later
        self.save_files()

        # Update the database to include the link to the docx file (for button functionality)
        self.db.add_file_path(self.job_id, self.file_path_CV_docx)
        
    # Save the files. Will allow different formats later
    def save_files(self):
        # Create application folders
        self.folder_path_json = rf"C:\Users\maxca\Desktop\tailor_my_CV\applications\{self.job_id}_{self.job_title}_{self.job_company}\json"
        self.folder_path_docx = rf"C:\Users\maxca\Desktop\tailor_my_CV\applications\{self.job_id}_{self.job_title}_{self.job_company}\docx"

        os.makedirs(self.folder_path_json, exist_ok=True)
        os.makedirs(self.folder_path_docx, exist_ok=True)

        self.file_path_CV_json = rf"{self.folder_path_json}\CV_{self.job_title}_{self.job_id}_V{self.version}.json"
        self.file_path_JobDescription_json = rf"{self.folder_path_json}\JobDescription_{self.job_title}_{self.job_id}_V{self.version}.json"
        self.file_path_CV_docx = rf"{self.folder_path_docx}\CV_{self.job_title}_{self.job_id}_V{self.version}.docx"

        # Write the job description json file to correct location
        with open(self.file_path_JobDescription_json, "w", encoding="utf-8") as f:
            f.write(self.job_summary.model_dump_json())

        # Write the new CV json file to correct location
        with open(self.file_path_CV_json, "w", encoding="utf-8") as f:
            f.write(self.new_CV.model_dump_json())

        # Generate word document template
        generate_docx(self.file_path_CV_docx, "templates/cv_template.docx", self.file_path_CV_json)
    


