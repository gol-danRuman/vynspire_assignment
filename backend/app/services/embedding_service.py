"""
Embedding service for generating vector representations of text.
Uses sentence-transformers for efficient local embeddings.
"""
from typing import List, Union
import logging
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings using sentence-transformers.
    Provides efficient batch processing and caching.
    """

    def __init__(self, model_name: str = None):
        """
        Initialize embedding service with specified model.

        Args:
            model_name: Name of the sentence-transformer model
        """
        self.model_name = model_name or settings.embedding_model
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """
        Load the sentence-transformer model.
        Lazy loading to avoid unnecessary initialization.
        """
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model loaded successfully. Dimension: {self.get_dimension()}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def get_dimension(self) -> int:
        """
        Get the dimensionality of the embedding vectors.

        Returns:
            int: Embedding dimension
        """
        if self.model is None:
            self._load_model()
        return self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            np.ndarray: Embedding vector

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        if self.model is None:
            self._load_model()

        try:
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalize for cosine similarity
            )
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate embeddings for a batch of texts.
        More efficient than processing individually.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once

        Returns:
            List[np.ndarray]: List of embedding vectors

        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Cannot embed empty text list")

        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if len(valid_texts) != len(texts):
            logger.warning(f"Filtered out {len(texts) - len(valid_texts)} empty texts")

        if not valid_texts:
            raise ValueError("All texts are empty")

        if self.model is None:
            self._load_model()

        try:
            logger.info(f"Generating embeddings for {len(valid_texts)} texts")
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=len(valid_texts) > 10  # Show progress for large batches
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def compute_similarity(
        self,
        embedding1: Union[np.ndarray, List[float]],
        embedding2: Union[np.ndarray, List[float]]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            float: Cosine similarity score (-1 to 1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Normalize if not already normalized
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)

        similarity = np.dot(vec1_norm, vec2_norm)
        return float(similarity)


# Global embedding service instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create the global embedding service instance.
    Implements singleton pattern for efficient model reuse.

    Returns:
        EmbeddingService: Global embedding service instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
