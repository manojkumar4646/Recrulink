"""
Pydantic request/response models for the RecruLink API.
These models define the schema for all API inputs and outputs,
providing automatic validation and documentation.
"""

from pydantic import BaseModel
from typing import Optional


# ---- Request Models ----

class JobDescriptionInput(BaseModel):
    """Input model for submitting a job description."""
    description: str


class MatchRequest(BaseModel):
    """Input model for matching candidates against a job description."""
    job_description: str
    top_k: int = 5


class AnalysisRequest(BaseModel):
    """Input model for generating AI analysis of a candidate."""
    candidate_id: int
    job_description: str


class QuestionsRequest(BaseModel):
    """Input model for generating interview questions for a candidate."""
    candidate_id: int
    job_description: str


# ---- Response Models ----

class UploadResponse(BaseModel):
    """Response model for the resume upload endpoint."""
    message: str
    filenames: list[str]
    candidate_ids: list[int]


class MatchResult(BaseModel):
    """A single candidate match result with similarity score and rank."""
    candidate_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    file_name: str
    similarity_score: float
    match_percentage: float
    rank: int


class MatchResponse(BaseModel):
    """Response model containing all match results."""
    matches: list[MatchResult]
    total_candidates: int


class AnalysisResponse(BaseModel):
    """Response model for AI-generated candidate analysis."""
    candidate_id: int
    match_percentage: float
    summary: str
    matching_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    weaknesses: list[str]
    years_of_experience: str = "N/A" 
    hiring_recommendation: str
    suitability_score: float


class InterviewQuestion(BaseModel):
    """A single interview question with a strategic rationale."""
    question: str
    rationale: str

class QuestionsResponse(BaseModel):
    """Response model for AI-generated interview questions."""
    candidate_id: int
    technical_questions: list[InterviewQuestion]
    project_questions: list[InterviewQuestion]
    behavioral_questions: list[InterviewQuestion]


class CandidateDetail(BaseModel):
    """Detailed information about a single candidate."""
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    file_name: str
    uploaded_at: str


class ClearResponse(BaseModel):
    """Response model for the clear-all endpoint."""
    message: str


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str