"""
Text extraction service for PDF and DOCX files.
Also extracts candidate metadata (name, email, phone) from resume text.
"""

import re
import os
from io import BytesIO

import fitz  # PyMuPDF
from docx import Document


class TextExtractor:
    """Extracts text content and metadata from resume files."""

    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """Extract all text from a PDF file using PyMuPDF."""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    @staticmethod
    def extract_from_docx(file_bytes: bytes) -> str:
        """Extract all paragraph text from a DOCX file using python-docx."""
        try:
            doc = Document(BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> str:
        """Route to the correct extractor based on file extension."""
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            return TextExtractor.extract_from_pdf(file_bytes)
        elif ext in [".docx", ".doc"]:
            return TextExtractor.extract_from_docx(file_bytes)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def extract_email(text: str) -> str | None:
        """Find an email address in the text using regex."""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_phone(text: str) -> str | None:
        """Find a phone number in the text using regex."""
        pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_name(text: str, filename: str) -> str:
        """
        Attempt to extract the candidate's name from the resume text.
        Falls back to deriving a name from the filename if detection fails.
        """
        # Check the first few lines for a likely name
        lines = [line.strip() for line in text.split('\n') if line.strip()][:5]
        skip_words = {
            'resume', 'cv', 'curriculum', 'vitae', 'email',
            'phone', 'address', 'contact', 'profile', 'objective'
        }

        for line in lines:
            words = line.split()
            if 2 <= len(words) <= 4:
                if not any(w.lower() in skip_words for w in words):
                    if not any(c in line for c in '@|#&*()[]{}:;/'):
                        return line

        # Fallback: convert filename to a human-readable name
        name = os.path.splitext(os.path.basename(filename))[0]
        name = name.replace('_', ' ').replace('-', ' ').title()
        return name