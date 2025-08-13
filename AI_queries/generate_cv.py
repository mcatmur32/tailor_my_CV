from openai import OpenAI
from pydantic import BaseModel, Field
#from typing import Annotated
import json
import os

def generate_cv(job_summary):

    client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
    )

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

    with open('inputs/master_cv.json', 'r', encoding="utf-8") as f:
        master_cv = json.load(f)

    master_cv_str = json.dumps(master_cv)
    #job_summary_str = json.dumps(job_summary)
    job_summary_str = job_summary

    # prompt = "Based on these 3 most important responsibilities from the job description, please tailor my CV for this position. Rewrite bullet points using the structure: 'Accomplished X by the measure Y that resulted in Z'. Do not make information up. Ensure it is compatible with latex (i.e. '\%', not just '%' etc). Here's my CV (in .json format):\n\n" + master_cv_str
    # prompt = "Based on the summarised job description below, please tailor my CV for this position. You may exclude anything you deem irrelevant, as well as slightly re-word and re-order descriptions in line with the job summary, but crucially DO NOT MAKE INFORMATION UP! Also, provide a detailed summary of changes made to the original. Here is the job summary: \n\n" + job_summary_str + "\n\nAnd here is my CV:\n\n" + master_cv_str

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
        {job_summary_str}

        ---

        ### 📄 Original CV:
        {master_cv_str}

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

    print(output)

    return output