"""
Unit tests for embedding service.
Tests embedding generation and similarity computation.
"""
import pytest
import numpy as np

from app.services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Test suite for EmbeddingService class."""

    @pytest.fixture
    def embedding_service(self):
        """Create embedding service instance for testing."""
        # Use a small model for faster tests
        return EmbeddingService(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def test_init(self, embedding_service):
        """Test service initialization."""
        assert embedding_service.model is not None
        assert embedding_service.model_name is not None

    def test_get_dimension(self, embedding_service):
        """Test getting embedding dimension."""
        dim = embedding_service.get_dimension()

        assert isinstance(dim, int)
        assert dim > 0
        assert dim == 384  # all-MiniLM-L6-v2 produces 384-dim vectors

    def test_embed_text_basic(self, embedding_service):
        """Test basic text embedding."""
        text = "This is a test sentence."
        embedding = embedding_service.embed_text(text)

        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 384
        assert embedding.dtype == np.float32 or embedding.dtype == np.float64

    def test_embed_text_empty_raises_error(self, embedding_service):
        """Test that empty text raises error."""
        with pytest.raises(ValueError, match="Cannot embed empty text"):
            embedding_service.embed_text("")

        with pytest.raises(ValueError, match="Cannot embed empty text"):
            embedding_service.embed_text("   ")

    def test_embed_text_normalization(self, embedding_service):
        """Test that embeddings are normalized."""
        text = "Test normalization."
        embedding = embedding_service.embed_text(text)

        # Check that embedding is approximately normalized
        norm = np.linalg.norm(embedding)
        assert 0.95 <= norm <= 1.05  # Allow small floating point error

    def test_embed_batch_basic(self, embedding_service):
        """Test batch embedding generation."""
        texts = [
            "First sentence.",
            "Second sentence.",
            "Third sentence."
        ]

        embeddings = embedding_service.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)

    def test_embed_batch_empty_list_raises_error(self, embedding_service):
        """Test that empty list raises error."""
        with pytest.raises(ValueError, match="Cannot embed empty text list"):
            embedding_service.embed_batch([])

    def test_embed_batch_filters_empty_strings(self, embedding_service):
        """Test that batch processing handles empty strings."""
        texts = ["Valid text", "", "Another valid text", "   "]

        # Should filter out empty strings and process valid ones
        embeddings = embedding_service.embed_batch(texts)

        assert len(embeddings) == 2  # Only 2 valid texts

    def test_embed_batch_all_empty_raises_error(self, embedding_service):
        """Test that all empty strings raises error."""
        texts = ["", "   ", "\n"]

        with pytest.raises(ValueError, match="All texts are empty"):
            embedding_service.embed_batch(texts)

    def test_compute_similarity_identical_texts(self, embedding_service):
        """Test similarity between identical embeddings."""
        text = "Test sentence."
        emb1 = embedding_service.embed_text(text)
        emb2 = embedding_service.embed_text(text)

        similarity = embedding_service.compute_similarity(emb1, emb2)

        assert isinstance(similarity, float)
        assert 0.99 <= similarity <= 1.0  # Should be very close to 1

    def test_compute_similarity_similar_texts(self, embedding_service):
        """Test similarity between similar texts."""
        text1 = "The cat sits on the mat."
        text2 = "A cat is sitting on a mat."

        emb1 = embedding_service.embed_text(text1)
        emb2 = embedding_service.embed_text(text2)

        similarity = embedding_service.compute_similarity(emb1, emb2)

        # Similar texts should have high similarity
        assert 0.7 <= similarity <= 1.0

    def test_compute_similarity_different_texts(self, embedding_service):
        """Test similarity between different texts."""
        text1 = "The weather is sunny today."
        text2 = "Quantum physics is fascinating."

        emb1 = embedding_service.embed_text(text1)
        emb2 = embedding_service.embed_text(text2)

        similarity = embedding_service.compute_similarity(emb1, emb2)

        # Different texts should have lower similarity
        assert -1.0 <= similarity <= 0.7

    def test_compute_similarity_with_lists(self, embedding_service):
        """Test similarity computation with list inputs."""
        emb1 = [0.1] * 384
        emb2 = [0.1] * 384

        similarity = embedding_service.compute_similarity(emb1, emb2)

        assert isinstance(similarity, float)
        assert 0.0 <= abs(similarity) <= 1.0

    def test_embedding_consistency(self, embedding_service):
        """Test that same text produces consistent embeddings."""
        text = "Consistency test."

        emb1 = embedding_service.embed_text(text)
        emb2 = embedding_service.embed_text(text)

        # Embeddings should be identical (or very close)
        difference = np.abs(emb1 - emb2).max()
        assert difference < 1e-5

    def test_batch_vs_individual_embeddings(self, embedding_service):
        """Test that batch and individual embeddings are consistent."""
        texts = ["First text.", "Second text."]

        # Generate embeddings individually
        individual_embs = [embedding_service.embed_text(t) for t in texts]

        # Generate embeddings in batch
        batch_embs = embedding_service.embed_batch(texts)

        # Compare
        for ind_emb, batch_emb in zip(individual_embs, batch_embs):
            difference = np.abs(np.array(ind_emb) - np.array(batch_emb)).max()
            assert difference < 1e-5


class TestEmbeddingServiceEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.fixture
    def embedding_service(self):
        """Create embedding service instance for testing."""
        return EmbeddingService(model_name="sentence-transformers/all-MiniLM-L6-v2")

    def test_very_long_text(self, embedding_service):
        """Test embedding very long text."""
        text = "word " * 1000  # Very long text

        embedding = embedding_service.embed_text(text)

        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 384

    def test_special_characters(self, embedding_service):
        """Test embedding text with special characters."""
        text = "Special chars: @#$%^&*()_+-={}[]|:;<>?,./~`"

        embedding = embedding_service.embed_text(text)

        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 384

    def test_unicode_text(self, embedding_service):
        """Test embedding unicode text."""
        text = "Unicode: 你好世界 مرحبا العالم Привет мир"

        embedding = embedding_service.embed_text(text)

        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 384

    def test_numbers_only(self, embedding_service):
        """Test embedding text with only numbers."""
        text = "1234567890"

        embedding = embedding_service.embed_text(text)

        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 384

    def test_large_batch(self, embedding_service):
        """Test processing large batch of texts."""
        texts = [f"Text number {i}" for i in range(100)]

        embeddings = embedding_service.embed_batch(texts, batch_size=16)

        assert len(embeddings) == 100
        assert all(len(emb) == 384 for emb in embeddings)
