from sqlalchemy.orm import Session
from database.models import Candidate, ResumeChunk
from embeddings.embedding_service import EmbeddingService
from rag.faiss_store import get_faiss_store

class RAGPipeline:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.faiss_store = get_faiss_store()

    def match_candidates(self, job_description: str, top_k: int, db: Session) -> list[dict]:
        # 1. Embed the Job Description using the Search Query instruction
        jd_embedding = self.embedding_service.embed_query(job_description)

        # 2. Search FAISS (each result is now a whole resume, not a chunk)
        scores, indices = self.faiss_store.search(jd_embedding, top_k)

        if len(indices) == 0:
            return []

        results = []
        seen_candidates = set()

        for score, faiss_idx in zip(scores, indices):
            if faiss_idx < 0:
                continue

            # Look up the candidate by their FAISS vector ID
            chunk = db.query(ResumeChunk).filter(ResumeChunk.faiss_index_id == int(faiss_idx)).first()
            if not chunk or chunk.candidate_id in seen_candidates:
                continue

            seen_candidates.add(chunk.candidate_id)

            # BGE-m3 baseline similarity is around 0.40 for unrelated text.
            # A true match will score 0.65 to 0.90+.
            # We filter out the "noise" matches below 0.50 (50%).
            if score < 0.50:
                continue

            candidate = db.query(Candidate).filter(Candidate.id == chunk.candidate_id).first()
            if candidate:
                results.append({
                    "candidate_id": candidate.id,
                    "name": candidate.name or "Unknown",
                    "email": candidate.email,
                    "phone": candidate.phone,
                    "file_name": candidate.file_name,
                    "similarity_score": round(float(score), 4),
                    "match_percentage": round(float(score) * 100, 2),
                })

        # Sort by score descending
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        for rank, result in enumerate(results, 1):
            result["rank"] = rank

        return results[:top_k]