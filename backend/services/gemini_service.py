"""
Gemini LLM service for AI-powered candidate analysis and interview question generation.
Uses Google's gemini-2.5-flash model via the google-generativeai SDK.
"""

import json
import os
import re

import google.generativeai as genai


class GeminiService:
    """Communicates with Gemini 2.5 Flash to analyze resumes and generate questions."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def analyze_candidate(self, resume_text: str, job_description: str) -> dict:
        """
        Generate a detailed AI analysis of a candidate's resume
        against a specific job description.

        Returns a dict with: match_percentage, summary, matching_skills,
        missing_skills, strengths, weaknesses, hiring_recommendation, suitability_score.
        """
        prompt = f"""You are an expert Technical Recruiter AI. Your job is to perform a strict, evidence-based analysis of a candidate's resume against a specific Job Description (JD).

Do not be generous. Be objective and factual. If a skill is not explicitly mentioned in the resume, consider it missing.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Step 1: Identify the absolute MUST-HAVE skills and requirements from the Job Description.
Step 2: Scan the resume for explicit evidence of those skills. 
Step 3: Calculate a strict match percentage based ONLY on how many JD requirements are met with evidence.

Provide your analysis in the following JSON format only. Do not include any text outside the JSON.
{{
    "match_percentage": <number 0-100, strictly based on JD requirements met>,
    "summary": "<1-2 sentence summary of who the candidate is and their overall fit for THIS specific role>",
    "matching_skills": ["<skill1 from JD found in resume>", "<skill2>"],
    "missing_skills": ["<skill1 from JD NOT found in resume>", "<skill2>"],
    "strengths": ["<specific strength relevant to the JD with brief evidence>", "<strength2>"],
    "weaknesses": ["<specific gap relevant to the JD>", "<weakness2>"],
    "years_of_experience": "<estimated total years of professional experience or 'N/A'>",
    "hiring_recommendation": "<Strong Hire | Hire | Maybe | Not Recommended>",
    "suitability_score": <number 0-10, one decimal place>
}}

Remember: 
- "matching_skills" must only contain skills actually requested in the JD and found in the resume.
- "missing_skills" must only contain skills requested in the JD but absent from the resume.
- Do not invent skills that are not in the resume."""        

        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text)
        except Exception as e:
            raise RuntimeError(f"Gemini analysis failed: {str(e)}")

    def generate_questions(self, resume_text: str, job_description: str) -> dict:
        """
        Generate targeted interview questions for a candidate
        based on their resume and the job description.

        Returns a dict with: technical_questions, project_questions, behavioral_questions.
        """
        prompt = f"""You are an expert Technical Interviewer AI. Your goal is to create a highly targeted interview guide for a candidate based on their resume and a specific Job Description.

Do not ask generic questions. Every question must have a specific strategic purpose based on the texts provided.

CANDIDATE RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Generate the interview questions in the following JSON format only. Do not include text outside the JSON.
{{
    "technical_questions": [
        {{"question": "The specific question to ask", "rationale": "Why we are asking: e.g., To verify claimed skill X or to probe technical gap Y"}}
    ],
    "project_questions": [
        {{"question": "The specific question about their project", "rationale": "Why we are asking: e.g., To understand their actual role in project Z"}}
    ],
    "behavioral_questions": [
        {{"question": "The specific behavioral question", "rationale": "Why we are asking: e.g., To assess culture fit or adaptability based on JD requirement"}}
    ]
}}

Guidelines:
- Technical Questions: Generate 4 questions. At least one MUST verify their strongest claimed skill. At least one MUST probe a technical gap between the resume and the JD.
- Project Questions: Generate 3 questions. Must be directly tied to the specific projects explicitly mentioned in the resume.
- Behavioral Questions: Generate 3 questions. Tailored to the soft skills, team dynamics, or seniority level mentioned in the JD.
"""        

        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text)
        except Exception as e:
            raise RuntimeError(f"Gemini question generation failed: {str(e)}")

    def _parse_json_response(self, text: str) -> dict:
        """
        Parse JSON from a Gemini response.
        Handles markdown code block wrappers that Gemini sometimes adds.
        """
        # Strip markdown code fences if present
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        cleaned = cleaned.strip()
        return json.loads(cleaned)