"""
SQLAlchemy ORM models for the RecruLink database.
Defines the schema for candidates, resume chunks, and job descriptions.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.connection import Base


class Candidate(Base):
    """
    Stores metadata for each uploaded candidate resume.
    Name, email, and phone are auto-extracted from resume text.
    """
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    file_name = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())


class ResumeChunk(Base):
    """
    Stores individual text chunks from resumes.
    Each chunk references its parent candidate and its position in the FAISS index.
    """
    __tablename__ = "resume_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    faiss_index_id = Column(Integer, nullable=False)


class JobDescription(Base):
    """Stores submitted job descriptions for reference and history."""
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())