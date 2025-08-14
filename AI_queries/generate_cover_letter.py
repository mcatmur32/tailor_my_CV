from openai import OpenAI
from pydantic import BaseModel, Field
import os

class CoverLetter(BaseModel):
    hook_paragraph: str
    main_section: str

def generate_cover_letter(job_summary: str, master_cv: str) -> CoverLetter:

    client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
    )

    system_prompt = f"""
        You are an expert Cover Letter writer with over 20 years of experience helping physics graduates write cover letters for industry roles in the UK. Your objective is to write a candidate's cover letter based on a provided job description summary in order to maximise relevance, professionalism, and showing a genuine interest in the job.

        You will be provided with:
        1. A JSON-formatted summary of a job description (including responsibilities, qualifications, and company values)
        2. A CV in JSON format

        ---

        ### 🔒 ESSENTIAL RULES:
        - Do NOT fabricate any experience, achievements, qualifications, or data.
        - Use perfect UK English spelling, grammar and tone.
        - Always maintain a natural and readable style.
        - Use 'and' instead of '&' if needed.

        ---

        ### ✏️ EDITING TASKS:
        - Write a hook paragraph. This is the first paragraph of the cover letter and should be designed to hook the reader. It should not be generic, and feel free to try some fancy sentence structure here.
        - Complete the main section. This can be multiple paragraphs if needed, but is the main part of the cover letter.
        - Avoid significant repetition of vocabulary throughout. If necessary, use synonyms.

        """


    user_prompt = f"""
        Here is the job summary and the original CV for reference:

        ---

        ### 📌 Job Summary:
        {job_summary}

        ---

        ### 📄 Original CV:
        {master_cv}

        """

    # Perform the request
    response = client.responses.parse(
        model="gpt-5-mini",
        input = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        text_format = CoverLetter
    )

    # Get the output
    output = response.output_parsed

    return output