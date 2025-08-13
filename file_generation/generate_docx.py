from docxtpl import DocxTemplate
import json

def generate_docx(file_path):
    # Load template
    doc = DocxTemplate("templates/cv_template.docx")

    # Load your JSON data
    with open("output_files/json/output_cv.json", "r", encoding="utf-8") as f:
        context = json.load(f)

    # Render into the template
    doc.render(context)

    # Save the filled CV
    doc.save(file_path)

#generate_docx()