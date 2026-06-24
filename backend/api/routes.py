"""
FastAPI route definitions for all RecruLink API endpoints.
Handles resume upload, job description submission, candidate matching,
AI analysis, interview question generation, and data management.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from database.models import Candidate, ResumeChunk, JobDescription
from services.resume_service import ResumeService
from rag.pipeline import RAGPipeline
from services.gemini_service import GeminiService
from rag.faiss_store import get_faiss_store
from api.models import (
    UploadResponse, JobDescriptionInput, MatchRequest, MatchResult,
    MatchResponse, AnalysisRequest, AnalysisResponse, QuestionsRequest,
    QuestionsResponse, CandidateDetail, ClearResponse, ErrorResponse
)

# API router with common prefix
router = APIRouter()

# Instantiate shared services (EmbeddingService uses singleton pattern)
resume_service = ResumeService()
rag_pipeline = RAGPipeline()
faiss_store = get_faiss_store()


def get_gemini_service() -> GeminiService:
    """Dependency that creates a GeminiService instance, or raises 500 if API key is missing."""
    try:
        return GeminiService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================== ENDPOINTS =====================


@router.post(
    "/upload-resumes",
    response_model=UploadResponse,
    summary="Upload and process resume files"
)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple resume files (PDF or DOCX).
    Each file is processed through the full RAG pipeline:
    text extraction, chunking, embedding, and storage.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    uploaded_filenames = []
    candidate_ids = []
    errors = []

    for file in files:
        if not file.filename:
            errors.append("A file has no filename")
            continue

        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in ['pdf', 'docx', 'doc']:
            errors.append(f"Unsupported format: {file.filename}")
            continue

        try:
            file_bytes = await file.read()
            candidate_id = resume_service.process_resume(file_bytes, file.filename, db)
            candidate_ids.append(candidate_id)
            uploaded_filenames.append(file.filename)
        except Exception as e:
            errors.append(f"Failed to process {file.filename}: {str(e)}")

    if not uploaded_filenames:
        raise HTTPException(
            status_code=500,
            detail=f"No resumes processed. Errors: {'; '.join(errors)}"
        )

    message = f"Successfully processed {len(uploaded_filenames)} resume(s)"
    if errors:
        message += f". {len(errors)} file(s) had errors"

    return UploadResponse(
        message=message,
        filenames=uploaded_filenames,
        candidate_ids=candidate_ids
    )


@router.post("/submit-job", summary="Store a job description")
async def submit_job(
    job_input: JobDescriptionInput,
    db: Session = Depends(get_db)
):
    """Save a job description to the database for record-keeping."""
    if not job_input.description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")

    job = JobDescription(description=job_input.description)
    db.add(job)
    db.commit()
    db.refresh(job)

    return {"message": "Job description saved", "job_id": job.id}


@router.post(
    "/match-candidates",
    response_model=MatchResponse,
    summary="Match candidates against a job description"
)
async def match_candidates(
    match_request: MatchRequest,
    db: Session = Depends(get_db)
):
    """
    Find the top-k candidates that best match a job description.
    Uses FAISS vector search with cosine similarity on BAAI/bge-m3 embeddings.
    """
    if not match_request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")

    if faiss_store.get_total_vectors() == 0:
        raise HTTPException(
            status_code=400,
            detail="No resumes uploaded yet. Please upload resumes first."
        )

    try:
        matches = rag_pipeline.match_candidates(
            job_description=match_request.job_description,
            top_k=match_request.top_k,
            db=db
        )

        total_candidates = db.query(Candidate).count()

        return MatchResponse(
            matches=[MatchResult(**m) for m in matches],
            total_candidates=total_candidates
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


@router.get(
    "/candidate/{candidate_id}",
    response_model=CandidateDetail,
    summary="Get candidate details by ID"
)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve metadata for a specific candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate with ID {candidate_id} not found"
        )

    return CandidateDetail(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        file_name=candidate.file_name,
        uploaded_at=str(candidate.uploaded_at)
    )


@router.post(
    "/generate-analysis",
    response_model=AnalysisResponse,
    summary="Generate AI candidate analysis"
)
async def generate_analysis(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Use Gemini 2.5 Flash to analyze a candidate's resume
    against a job description. Returns match percentage, skills assessment,
    strengths, weaknesses, and hiring recommendation.
    """
    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate with ID {request.candidate_id} not found"
        )

    try:
        resume_text = resume_service.get_full_resume_text(request.candidate_id, db)
        gemini = get_gemini_service()
        analysis = gemini.analyze_candidate(resume_text, request.job_description)

        return AnalysisResponse(
            candidate_id=request.candidate_id,
            match_percentage=analysis.get("match_percentage", 0),
            summary=analysis.get("summary", ""),
            matching_skills=analysis.get("matching_skills", []),
            missing_skills=analysis.get("missing_skills", []),
            strengths=analysis.get("strengths", []),
            weaknesses=analysis.get("weaknesses", []),
            years_of_experience=analysis.get("years_of_experience", "N/A"),
            hiring_recommendation=analysis.get("hiring_recommendation", "Maybe"),
            suitability_score=analysis.get("suitability_score", 0)
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post(
    "/generate-questions",
    response_model=QuestionsResponse,
    summary="Generate interview questions"
)
async def generate_questions(
    request: QuestionsRequest,
    db: Session = Depends(get_db)
):
    """
    Use Gemini 2.5 Flash to generate targeted interview questions
    (technical, project-based, and behavioral) for a specific candidate.
    """
    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate with ID {request.candidate_id} not found"
        )

    try:
        resume_text = resume_service.get_full_resume_text(request.candidate_id, db)
        gemini = get_gemini_service()
        questions = gemini.generate_questions(resume_text, request.job_description)

        return QuestionsResponse(
            candidate_id=request.candidate_id,
            technical_questions=[
                InterviewQuestion(**q) for q in questions.get("technical_questions", [])
            ],
            project_questions=[
                InterviewQuestion(**q) for q in questions.get("project_questions", [])
            ],
            behavioral_questions=[
                InterviewQuestion(**q) for q in questions.get("behavioral_questions", [])
            ]
        )
           
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")


@router.get("/candidates", response_model=list[CandidateDetail], summary="List all candidates")
async def list_candidates(db: Session = Depends(get_db)):
    """Retrieve a list of all uploaded candidates, ordered by most recent first."""
    candidates = db.query(Candidate).order_by(Candidate.uploaded_at.desc()).all()
    return [
        CandidateDetail(
            id=c.id,
            name=c.name,
            email=c.email,
            phone=c.phone,
            file_name=c.file_name,
            uploaded_at=str(c.uploaded_at)
        )
        for c in candidates
    ]


@router.delete("/clear", response_model=ClearResponse, summary="Clear all data")
async def clear_all(db: Session = Depends(get_db)):
    """
    Delete all candidates, resume chunks, job descriptions from MySQL
    and reset the FAISS vector index.
    """
    try:
        db.query(ResumeChunk).delete()
        db.query(Candidate).delete()
        db.query(JobDescription).delete()
        db.commit()

        faiss_store.reset()

        return ClearResponse(message="All data cleared successfully")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")


@router.get("/health", summary="Health check")
async def health_check():
    """Check if the API and FAISS index are operational."""
    return {
        "status": "healthy",
        "faiss_vectors": faiss_store.get_total_vectors()
    }