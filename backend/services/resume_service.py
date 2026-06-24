from sqlalchemy.orm import Session
from database.models import Candidate, ResumeChunk
from services.text_extractor import TextExtractor
from embeddings.embedding_service import EmbeddingService
from rag.faiss_store import get_faiss_store

class ResumeService:
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.embedding_service = EmbeddingService()
        self.faiss_store = get_faiss_store()

    def process_resume(self, file_bytes: bytes, filename: str, db: Session) -> int:
        # 1. Extract full text
        text = self.text_extractor.extract_text(file_bytes, filename)
        if not text:
            raise ValueError(f"No text extracted from {filename}")

        # 2. Extract metadata
        name = self.text_extractor.extract_name(text, filename)
        email = self.text_extractor.extract_email(text)
        phone = self.text_extractor.extract_phone(text)

        # 3. Save Candidate to MySQL
        candidate = Candidate(name=name, email=email, phone=phone, file_name=filename)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        # 4. Embed the ENTIRE resume as a single document (NO CHUNKING)
        # This preserves the full context of skills and experience together.
        embeddings = self.embedding_service.embed_documents([text])

        # 5. Store the single vector in FAISS
        faiss_ids = self.faiss_store.add_embeddings(embeddings)

        # 6. Store the full text in MySQL linked to the FAISS vector
        chunk_record = ResumeChunk(
            candidate_id=candidate.id,
            chunk_text=text,
            faiss_index_id=faiss_ids[0]
        )
        db.add(chunk_record)
        db.commit()

        return candidate.id

    def get_full_resume_text(self, candidate_id: int, db: Session) -> str:
        chunks = db.query(ResumeChunk).filter(ResumeChunk.candidate_id == candidate_id).all()
        if not chunks:
            raise ValueError(f"No resume data found for candidate ID {candidate_id}")
        return "\n\n".join([chunk.chunk_text for chunk in chunks])