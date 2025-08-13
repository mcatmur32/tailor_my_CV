import tkinter as tk
from tkinter import scrolledtext
from AI_queries.generate_cv import generate_cv
from AI_queries.summarise_job import summarise_job
from file_generation.generate_docx import generate_docx

# Create main application window
root = tk.Tk()
root.title("Job Description Processor")
root.geometry("1000x700")  # width x height

# Create label
label = tk.Label(root, text="Paste job description below:", font=("Arial", 14))
label.pack(pady=10)

# Create a large scrollable text box
text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), height=10)
text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)




# Define submit function
def process_text():
    job_description = text_box.get("1.0", tk.END).strip()

    job_summary = summarise_job(job_description)

    print(job_summary)
    print("\n\n")

    new_CV = generate_cv(job_summary)

    with open("output_files/json/output_cv.json", "w", encoding="utf-8") as f:
        f.write(new_CV.model_dump_json())

    generate_docx()

    
    # Read the generated LaTeX file
    """try:
        with open("output_cv.tex", "r", encoding="utf-8") as f:
            tex_content = f.read()
    except FileNotFoundError:
        tex_content = "Error: .tex file not found."
    
    # Show output in the output_text_box
    output_text_box_cv.delete("1.0", tk.END)
    output_text_box_cv.insert(tk.END, tex_content)

    output_text_box_cover_letter.delete("1.0", tk.END)
    # output_text_box_cover_letter.insert(tk.END, cover_letter)

    #generate_pdf("output_cv.tex")"""


# Create Submit Button
submit_btn = tk.Button(root, text="Generate CV", command=process_text, font=("Arial", 12), bg="#4CAF50", fg="white")
submit_btn.pack(pady=10)

# Label for output
output_label = tk.Label(root, text="Generated LaTeX output:", font=("Arial", 14))
output_label.pack(pady=(20, 5))

# Output text box (scrollable)
output_text_box_cv = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier New", 12), height=20)
output_text_box_cv.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)

output_text_box_cover_letter = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier New", 12), height=20)
output_text_box_cover_letter.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)

# Run the application
root.mainloop()