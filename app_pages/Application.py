from datetime import datetime
from pathlib import Path

from database.Database import Database

from AI_queries.generate_cv import generate_cv
from AI_queries.summarise_job import summarise_job
from AI_queries.generate_cover_letter import generate_cover_letter
from file_generation.generate_docx import generate_docx

class Application():
    def __init__(self, job_data: dict, master_cv: dict, db: Database):
        # Inputted data
        self.master_cv = master_cv

        # Database
        self.db = db

        # Standardised schema
        self.data = {
            "job_details": {
                "title": job_data.get("title", ""),
                "company": job_data.get("company", ""),
                "location": job_data.get("location", ""),
                "deadline": job_data.get("deadline", ""),
                "status": job_data.get("status", "Draft"),
                "description": job_data.get("description", "")
            },
            "summary": {},
            "CV": {},
            "cover_letter": {},
            "metadata": {
                "ai_model": "gpt-5-mini"
            }
        }

    def generateJobSummary(self):
        self.data["summary"] = summarise_job(self.job_data["description"])
        # self.job_summary = {k: v for k, v in self.job_data.items() if k in ["title", "company", "deadline", "description"]} | self.job_summary

    def generateCV(self):
        self.job_summary = self.data["job_details"] | self.data["summary"]
        self.new_CV = generate_cv(self.job_summary, self.master_cv)

    def generateCoverLetter(self):
        self.new_cover_letter = generate_cover_letter(self.job_summary, self.master_cv)

    def addApplication(self):
        self.job_id = self.db.new_entry(self.job_data["company"], self.job_data["title"], self.job_data["deadline"], self.job_data["status"])
        return self.job_id
    
    def 
    
    



    

