from PyQt5.QtWidgets import QTextEdit, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox

from AI_queries.generate_cv import generate_cv
from AI_queries.summarise_job import summarise_job
from file_generation.generate_docx import generate_docx

class NewApplicationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Big Textbox Example")

        main_layout = QVBoxLayout()

        # Multi-line textbox
        self.job_desc_textbox = QTextEdit()
        self.job_desc_textbox.setPlaceholderText("Type your text here...")  # optional placeholde
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
        job_description = self.job_desc_textbox.toPlainText()
        job_summary = summarise_job(job_description)

        print(job_summary)
        print("\n\n")

        new_CV = generate_cv(job_summary)

        with open("output_files/json/output_cv.json", "w", encoding="utf-8") as f:
            f.write(new_CV.model_dump_json())

        generate_docx()