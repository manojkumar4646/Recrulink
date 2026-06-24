"""
RecruLink FastAPI application entry point.
Configures the app, CORS middleware, startup events, and includes API routes.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database.connection import init_db
from api.routes import router

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs initialization tasks on startup (create DB tables)
    and cleanup tasks on shutdown.
    """
    print("Starting RecruLink backend...")
    init_db()
    print("Database tables initialized.")
    yield
    print("Shutting down RecruLink backend...")


# Create the FastAPI application instance
app = FastAPI(
    title="RecruLink – RAG-Based Resume Matching System",
    description=(
        "AI-powered resume matching using Retrieval-Augmented Generation (RAG), "
        "FAISS vector search with BAAI/bge-m3 embeddings, and Gemini 2.5 Flash LLM."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for all origins (suitable for development; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routes under the /api prefix
app.include_router(router, prefix="/api", tags=["RecruLink API"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint that confirms the API is running."""
    return {
        "name": "RecruLink API",
        "version": "1.0.0",
        "description": "RAG-Based Resume Matching System",
        "docs": "/docs"
    }