from openai import OpenAI
from pydantic import BaseModel, Field
import os

class Education(BaseModel):
    degree: str
    institution: str
    location: str
    start_date: str
    end_date: str
    grade: str
    description: list[str] = Field(..., min_length=3, max_length=5)

class WorkExperience(BaseModel):
    title: str
    company: str
    location: str
    start_date: str
    end_date: str
    description: list[str] = Field(..., min_length=3, max_length=5)

class Project(BaseModel):
    title: str
    start_date: str
    end_date: str
    description: list[str] = Field(..., min_length=3, max_length=5)

class Skills(BaseModel):
    languages: list[str]
    libraries: list[str]
    tools: list[str]
    soft_skills: list[str]
    interests: list[str]

class CV(BaseModel):
    profile: str
    education: list[Education]
    work_experience: list[WorkExperience]
    projects: list[Project]
    skills: Skills

def generate_cv(job_summary: str, master_cv: str) -> CV:

    client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
    )

    system_prompt = f"""
        You are an expert CV writer with over 20 years of experience helping physics graduates tailor their CVs for industry roles in the UK. Your objective is to rewrite a candidate's CV based on a provided job description summary in order to maximise relevance, professionalism, and ATS (Applicant Tracking System) compatibility.

        You will be provided with:
        1. A JSON-formatted summary of a job description (including responsibilities, qualifications, and company values)
        2. A CV in JSON format

        ---

        ### 🔒 ESSENTIAL RULES:
        - Do NOT fabricate any experience, achievements, qualifications, or data.
        - **ALWAYS** include quantified data if provided, but do NOT invent numbers unless explicitly provided.
        - Only use education/work experience/projects within their designated sections, i.e. do not move them to different sections.
        - Use perfect UK English spelling, grammar and tone.
        - Always maintain a natural and readable style.
        - Profile section must be no more than 60 words long.
        - Remove content irrelevant to the job application.
        - Ensure **at least 3 bullet points per education/work experience/project, maximum 5 bullet points**.
        - CV must be no more than 2 pages. This is approximately 5 work experiences/projects chosen in total.
        - Use 'and' instead of '&' if needed.

        ---

        ### ✏️ EDITING TASKS:
        - Incorporate the job title and relevant phrasing into the profile section.
        - Infuse ATS keywords from the job summary naturally throughout the CV.
        - Avoid significant repetition of vocabulary throughout. If necessary, use synonyms.
        - Use **reverse-chronological order** for all sections (experience, education and projects).
        - Group soft and technical skills into concise, scannable sections.

        """


    user_prompt = f"""
        Here is the job summary and the original CV for tailoring:

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
        text_format = CV
    )

    # Get the output
    output = response.output_parsed

    return output