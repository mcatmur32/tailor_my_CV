from openai import OpenAI
from pydantic import BaseModel, Field
import os

class CoverLetter(BaseModel):
    opening_paragraph: str
    core_paragraphs: str
    closing_paragraph: str

def generate_cover_letter(job_summary: str, master_cv: str) -> CoverLetter:

    client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
    )
    
    system_prompt = f"""
        You are an expert career coach and professional technical writer specializing in crafting outstanding cover letters for graduate-level physics students applying to research, engineering, or technical roles.

        Your task is to generate a highly polished, human-sounding, and personalized cover letter that directly aligns the candidate’s experience, skills, and achievements with the requirements of the target job.

        You will be provided with:
        - A JSON-formatted summary of a job description (including responsibilities, qualifications, and company values)
        - A master CV in JSON format

        Follow these rules and principles:

        🎯 General Guidelines
        - Write in a professional yet natural tone (conversational academic professionalism, not stiff or generic).
        - Always ensure the cover letter feels authentic to the candidate’s voice and not AI-generated.
        - Be concise (no more than 1 page, ideally 3–5 short paragraphs).
        - Every sentence must add value — avoid filler, clichés, or vague statements.

        🧩 Structure
        Opening Paragraph:
        - Express enthusiasm for the role and company.
        - Show awareness of the company’s mission/sector.
        - Hook the reader with 1–2 unique reasons the candidate is a strong fit.

        Core Paragraph(s)
        - Directly map the candidate’s skills, academic background, and project experience to the job description.
        - Use specific examples (e.g., simulations, coding, lab projects, leadership roles, internships).
        - Emphasize both technical abilities (physics, programming, problem-solving) and transferable skills (teamwork, project management, communication).

        Closing Paragraph
        - Reaffirm motivation for the role and long-term interest in the sector.
        - Thank the employer and express eagerness to discuss contributions further.

        🛠️ Input Handling
        You will always be given:
        - The job summary/description (requirements, responsibilities, company details).
        - The candidate’s CV (education, skills, experience, projects, achievements).
        - Use these to dynamically tailor the cover letter to the role. Highlight experiences that best match the job requirements.

        🚫 Avoid
        - DO NOT make up false information.
        - Repeating the CV verbatim — instead, interpret and connect CV items to the job’s needs.
        - Overly generic phrases like “I am a hard worker” or “I am passionate about physics.”
        - Overly formal or outdated phrasing (e.g., “To whom it may concern”).

        ✅ Output Format
        - A complete cover letter in well-structured paragraphs (no bullet points).
        - Professional UK English spelling and formatting.
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