"""
Database configuration and session management.
Handles PostgreSQL connection with pgvector extension.
"""
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.debug
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session.
    Ensures proper session cleanup after use.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database schema and enable pgvector extension.
    Creates all tables and ensures pgvector is available.
    """
    try:
        # Enable pgvector extension
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("pgvector extension enabled successfully")

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
