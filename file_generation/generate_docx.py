from docxtpl import DocxTemplate
import json

def generate_docx(file_path: str, template_path: str, json_path: str) -> DocxTemplate:
    # Load template
    doc = DocxTemplate(template_path)

    # Load your JSON data
    with open(json_path, "r", encoding="utf-8") as f:
        context = json.load(f)

    # Render into the template
    doc.render(context)

    # Save the filled CV
    doc.save(file_path)

    return doc

#generate_docx()