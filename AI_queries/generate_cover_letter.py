from openai import OpenAI
from pydantic import BaseModel, Field
import os

class CoverLetter(BaseModel):
    opening_paragraph: str
    core_paragraphs: str
    closing_paragraph: str

class Critiquer(BaseModel):
    score: int
    strengths: list[str]
    improvements: list[str]

def generate_cover_letter(job_summary: str, master_cv: str, critique_mode: bool) -> CoverLetter:

    client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
    )
    
    system_prompt_writer = f"""
        You are an expert career coach and professional technical writer specializing in crafting outstanding cover letters for graduate-level physics students applying to research, engineering, or technical roles.

        Your task is to generate a highly polished, human-sounding, and personalized cover letter that directly aligns the candidate’s experience, skills, and achievements with the requirements of the target job.

        You will be provided with:
        - A JSON-formatted summary of a job description (including responsibilities, qualifications, and company values)
        - A master CV in JSON format

        You may also be provided with:
        - Feedback from an expert cover letter critiquer for a draft cover letter

        Follow these rules and principles:

        🎯 General Guidelines
        - Write in a professional yet natural tone (conversational academic professionalism, not stiff or generic).
        - Always ensure the cover letter feels authentic to the candidate’s voice and not AI-generated.
        - Be concise (no more than 1 page, ideally 3–5 short paragraphs).
        - Every sentence must add value — avoid filler, clichés, or vague statements.
        - Respond to the feedback provided

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


    user_prompt_writer = f"""
        Here is the job summary and the original master CV for reference:

        ---

        ### 📌 Job Summary:
        {job_summary}

        ---

        ### 📄 Original CV:
        {master_cv}

    """

    if critique_mode:
        MAX_ITERATION_NUM = 3
        MIN_SCORE = 9

        system_prompt_critiquer = f"""
            You are a strict hiring manager evaluating graduate-level cover letters.
            Your task is to critically score and provide feedback on a candidate's cover letter.

            ### Scoring Rules:
            - Score the cover letter from 1 to 10.
            - A score of 10 means the letter is outstanding: well-structured, concise, tailored to the job, professional, and engaging.
            - A score of 9 is excellent but with very minor areas to polish.
            - A score of 7-8 is good but needs clear improvements.
            - A score of 5-6 is mediocre and may not impress an employer.
            - A score below 5 is weak, unfocused, or poorly written.

            ### Feedback Rules:
            - Be concise and specific.
            - Identify the main strengths and improvements.

        """

        for i in range(MAX_ITERATION_NUM):
            print(i)
            # Perform the request
            response = client.responses.parse(
                model="gpt-5-mini",
                input = [
                    {"role": "system", "content": system_prompt_writer},
                    {"role": "user", "content": user_prompt_writer}
                ],
                text_format = CoverLetter
            )

            # Get the output
            draft = response.output_parsed

            user_prompt_critiquer = f"""
                Here is the job summary, master CV and the current cover letter draft for reference:

                ---

                ### 📌 Job Summary:
                {job_summary}

                ---

                ### 📄 Original CV:
                {master_cv}

                ---

                ### 📄 Cover Letter Draft:
                {draft.model_dump_json()}

            """

            critique = client.responses.parse(
                model="gpt-5-mini",
                input = [
                    {"role": "system", "content": system_prompt_critiquer},
                    {"role": "user", "content": user_prompt_critiquer}
                ],
                text_format = Critiquer
            )

            critique = critique.output_parsed
            new_score = critique.score

            print(new_score)
            print(critique.strengths)
            print(critique.improvements)
            print("\n")

            if new_score >= MIN_SCORE:
                break

            user_prompt_writer = f"""
                Here is the draft cover letter and critiquer feedback, along with the job summary and master CV for reference:

                ---

                ### 📄 Draft cover letter:
                {draft.model_dump_json()}

                ---

                ### 📌 Feedback:
                {critique.model_dump_json()}

                ---

                ### 📌 Job Summary:
                {job_summary}

                ---

                ### 📄 Original CV:
                {master_cv}

            """

        final_output = draft

    else:
        # Perform the request
        response = client.responses.parse(
            model="gpt-5-mini",
            input = [
                {"role": "system", "content": system_prompt_writer},
                {"role": "user", "content": user_prompt_writer}
            ],
            text_format = CoverLetter
        )

        # Get the output
        final_output = response.output_parsed
        
    return final_output