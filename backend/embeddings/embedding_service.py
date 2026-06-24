import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = SentenceTransformer("BAAI/bge-m3")
        return cls._instance

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        """Embed full resumes as documents."""
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """Embed Job Description as a search query. BGE requires this prefix for accuracy."""
        instructed_query = "Represent this sentence for searching relevant passages: " + query
        embedding = self.model.encode([instructed_query], normalize_embeddings=True, show_progress_bar=False)
        return embedding[0]

    @staticmethod
    def get_dimension() -> int:
        return 1024