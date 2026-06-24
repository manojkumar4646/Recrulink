"""
FAISS vector index manager.
Handles storing, searching, and persisting vector embeddings.
"""

import os
import faiss
import numpy as np


class FAISSStore:
    """Manages a FAISS IndexFlatIP index for storing and searching vectors."""

    def __init__(self):
        self.dimension = 1024
        self.index_dir = os.getenv("FAISS_INDEX_PATH", "faiss_index")
        self.index_file = os.path.join(self.index_dir, "index.faiss")
        self.index = self._load_or_create_index()

    def _load_or_create_index(self) -> faiss.IndexFlatIP:
        if os.path.exists(self.index_file):
            return faiss.read_index(self.index_file)
        return faiss.IndexFlatIP(self.dimension)

    def add_embeddings(self, embeddings: np.ndarray) -> list[int]:
        start_id = self.index.ntotal
        self.index.add(embeddings.astype(np.float32))
        self.save()
        return list(range(start_id, start_id + len(embeddings)))

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        query = query_embedding.reshape(1, -1).astype(np.float32)
        search_k = min(top_k * 5, self.index.ntotal)
        if search_k == 0:
            return np.array([]), np.array([])
        scores, indices = self.index.search(query, max(search_k, 1))
        return scores[0], indices[0]

    def save(self):
        os.makedirs(self.index_dir, exist_ok=True)
        faiss.write_index(self.index, self.index_file)

    def get_total_vectors(self) -> int:
        return self.index.ntotal

    def reset(self):
        self.index = faiss.IndexFlatIP(self.dimension)
        if os.path.exists(self.index_file):
            os.remove(self.index_file)
        self.save()


# ==========================================
# SINGLETON PATTERN: Share ONE instance
# ==========================================
_instance = None

def get_faiss_store() -> FAISSStore:
    """Returns a single shared FAISSStore instance across the entire app."""
    global _instance
    if _instance is None:
        _instance = FAISSStore()
    return _instance