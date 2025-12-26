"""
Configuration management for the RAG application.
Loads settings from environment variables with validation.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with validation and type safety."""

    # Database
    database_url: str = Field(
        default="postgresql://raguser:ragpassword@localhost:5432/ragdb",
        description="PostgreSQL connection string"
    )

    # Google Gemini
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key for LLM integration"
    )

    # File Upload
    upload_dir: str = Field(
        default="./uploads",
        description="Directory for uploaded files"
    )
    max_upload_size: int = Field(
        default=10485760,
        description="Maximum file upload size in bytes (10MB)"
    )

    # Document Processing
    chunk_size: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Number of characters per chunk"
    )
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Character overlap between chunks"
    )

    # Retrieval
    top_k_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of chunks to retrieve for context"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings"
    )

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    debug: bool = Field(default=True, description="Debug mode")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins"
    )

    # LLM Settings
    gemini_model: str = Field(
        default="gemini-pro",
        description="Gemini model to use"
    )
    max_tokens: int = Field(
        default=1024,
        ge=100,
        le=2048,
        description="Maximum tokens for LLM response"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="LLM temperature for response generation"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("chunk_overlap")
    def validate_overlap(cls, v, values):
        """Ensure overlap is less than chunk size."""
        if "chunk_size" in values and v >= values["chunk_size"]:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v


# Global settings instance
settings = Settings()
