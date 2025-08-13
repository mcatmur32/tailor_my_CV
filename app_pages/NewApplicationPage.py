from PyQt5.QtWidgets import QLineEdit, QTextEdit, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox

from AI_queries.generate_cv import generate_cv
from AI_queries.summarise_job import summarise_job
from file_generation.generate_docx import generate_docx

import sqlite3

class NewApplicationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Application Page")

        main_layout = QVBoxLayout()

        # Single line job title textbok
        self.job_title_textbox = QLineEdit()
        self.job_title_textbox.setPlaceholderText("Add job title here")
        main_layout.addWidget(self.job_title_textbox)

        # Multi-line job description textbox
        self.job_desc_textbox = QTextEdit()
        self.job_desc_textbox.setPlaceholderText("Add job description here")
        main_layout.addWidget(self.job_desc_textbox, stretch=2)

        # Checkboxes
        checkbox_layout = QHBoxLayout()
        self.CV_checkbox = QCheckBox("CV")
        self.cover_letter_checkbox = QCheckBox("Cover Letter")
        checkbox_layout.addWidget(self.CV_checkbox)
        checkbox_layout.addWidget(self.cover_letter_checkbox)
        main_layout.addLayout(checkbox_layout, stretch=1)

        # Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.process_text)
        main_layout.addWidget(self.submit_button, stretch=1)

        self.setLayout(main_layout)

    def process_text(self):
        self.title = "Test"
        self.job_description = self.job_desc_textbox.toPlainText()
        self.version = 1
        self.job_summary = summarise_job(self.job_description)

        #print(self.job_summary)
        print("\n\n")

        self.new_CV = generate_cv(self.job_summary)

        with open("output_files/json/output_cv.json", "w", encoding="utf-8") as f:
            f.write(self.new_CV.model_dump_json())

        

        self.submit_to_database()


    def submit_to_database(self):
        # Connect to the database
        conn = sqlite3.connect('database/my_database.db')
        cursor = conn.cursor()

        # Create a table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                title TEXT NOT NULL,
                CV_path TEXT,
                CV_version INTEGER,
                cover_letter_path TEXT,
                cover_letter_version INTEGER,
                deadline TEXT,
                status INTEGER
                
            )
        ''')

        cursor.execute("INSERT INTO job_applications (company, title, CV_path, CV_version, cover_letter_path, cover_letter_version, deadline, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ("My Inc.", self.title, "", self.version, "", 1, "TBC", 0))
        entry_id = cursor.lastrowid

        file_path = rf"C:\Users\maxca\Desktop\tailor_my_CV\output_files\docx\CV_{self.title}_{entry_id}_V{self.version}.docx"

        generate_docx(file_path)

        cursor.execute("UPDATE job_applications SET CV_path = ? WHERE id = ?", (file_path, entry_id))

        
        
        conn.commit()
        print("success")

        #conn.close()