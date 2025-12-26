"""
Pytest configuration and fixtures for testing.
Provides reusable test fixtures and setup/teardown logic.
"""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app
from app.models.document import Document, DocumentChunk


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create a test database session.
    Uses SQLite in-memory for isolated tests.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> TestClient:
    """
    Create a test client with database override.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_document(test_db: Session) -> Document:
    """
    Create a sample document for testing.
    """
    document = Document(
        filename="test.txt",
        file_type=".txt",
        file_size=1024,
        chunk_count=2
    )
    test_db.add(document)
    test_db.commit()
    test_db.refresh(document)
    return document


@pytest.fixture
def sample_chunks(test_db: Session, sample_document: Document) -> list:
    """
    Create sample chunks for testing.
    Note: SQLite doesn't support vector type, so we'll mock embeddings.
    """
    chunks = [
        DocumentChunk(
            document_id=sample_document.id,
            chunk_index=0,
            content="This is the first chunk of text.",
            embedding=[0.1] * 384  # Mock embedding
        ),
        DocumentChunk(
            document_id=sample_document.id,
            chunk_index=1,
            content="This is the second chunk of text.",
            embedding=[0.2] * 384  # Mock embedding
        )
    ]

    for chunk in chunks:
        test_db.add(chunk)

    test_db.commit()

    for chunk in chunks:
        test_db.refresh(chunk)

    return chunks


@pytest.fixture
def sample_text_file(tmp_path):
    """
    Create a temporary text file for testing.
    """
    file_path = tmp_path / "test.txt"
    content = "This is a test document.\nIt has multiple lines.\nFor testing purposes."
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def sample_pdf_file(tmp_path):
    """
    Create a temporary PDF file for testing.
    """
    # Note: This is a mock - real PDF testing would require PyPDF2
    file_path = tmp_path / "test.pdf"
    file_path.write_bytes(b"Mock PDF content")
    return str(file_path)
