"""
Text chunking service using LangChain's RecursiveCharacterTextSplitter.
Splits long resume texts into overlapping chunks for better embedding coverage.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkService:
    """Splits text into manageable chunks with overlap for context preservation."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 150):
        """
        Args:
            chunk_size: Maximum number of characters per chunk.
            chunk_overlap: Number of overlapping characters between chunks.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks. Returns the full text as a single chunk if splitting fails."""
        chunks = self.splitter.split_text(text)
        return chunks if chunks else [text]