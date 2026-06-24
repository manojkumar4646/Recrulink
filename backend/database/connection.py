"""
Database connection management using SQLAlchemy.
Creates the engine, session factory, and Base class for ORM models.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Build MySQL connection URL from environment variables
DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER', 'root')}:"
    f"{os.getenv('MYSQL_PASSWORD', 'rootpassword')}@"
    f"{os.getenv('MYSQL_HOST', 'localhost')}:"
    f"{os.getenv('MYSQL_PORT', '3306')}/"
    f"{os.getenv('MYSQL_DATABASE', 'recrulink')}"
)

# Create SQLAlchemy engine with connection pooling and auto-reconnect
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # Check connection health before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=False              # Set True for SQL query logging
)

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables defined by ORM models."""
    # Import models so they are registered with Base.metadata
    from database.models import Candidate, ResumeChunk, JobDescription  # noqa: F401
    Base.metadata.create_all(bind=engine)