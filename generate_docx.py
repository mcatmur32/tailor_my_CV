from docxtpl import DocxTemplate
import json

def generate_docx():
    # Load template
    doc = DocxTemplate("cv_template.docx")

    # Load your JSON data
    with open("output_cv.json", "r", encoding="utf-8") as f:
        context = json.load(f)

    # Render into the template
    doc.render(context)

    # Save the filled CV
    doc.save("filled_cv.docx")

#generate_docx()