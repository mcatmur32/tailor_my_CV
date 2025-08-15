from openai import OpenAI
from pydantic import BaseModel
import os
import json

# Defines the job summary json format outputted by the AI
class JobDescriptor(BaseModel):
    job_title: str
    company_name: str
    industry: str
    location: str
    essential_requirements: list[str]
    preferred_requirements: list[str]
    hard_skills: list[str]
    soft_skills: list[str]
    ATS_keywords: list[str]
    key_responsibilities: list[str]
    tools_and_technologies: list[str]
    company_values: list[str]
    tailoring_recommendations: list[str]

# Reads in job description and summarises the key details into a json format
def summarise_job (description: str) -> JobDescriptor:

    # Connect to API
    client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
    )

    

    # Prompt passed into the AI
    prompt = "Given the following job description, extract key information from it and return it in the format specified. \nUse natural language understanding to infer values, tone, responsibilities, and include recommended tailoring strategies even if not explicitly stated, as well as some ATS-friendly keywords/phrases someone should include in their CV when applying to this job. Here is the job description:\n\n" + description
    
    system_prompt = f"""
        You are an expert job description analyst with over 20 years of experience. You will be given a job description, and you must summarise it as follows:

        - Include the core information: job title, company name, industry, and location.
        - All essential and preferred requirements for the job.
        - All the hard skills and soft skills required to do such a job.
        - Keywords in the job description that an Applicant Tracking System (ATS) would pick up on if applying to the job.
        - 3 key responsibilities that would be required on the job.
        - The tools and technologies used on the job.
        - Company values.
        - Finally, any recommendations when it comes to tailoring a CV to this job.

    """

    user_propmpt = f"""
        Here is the job description for summarising:

        ---

        ### 📌 Job Description:
        {description}
    """

    # Perform the request
    response = client.responses.parse(
        model="gpt-5-mini",
        input = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_propmpt}
        ],
        text_format = JobDescriptor
    )

    # Get the output
    job_summary = response.output_parsed

    # job_summary = output.json(indent=2)
    # job_summary = json.dumps(output.model_dump(), indent=2)

    return job_summary