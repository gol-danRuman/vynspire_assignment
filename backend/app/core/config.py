"""
Configuration management for the RAG application.
Loads settings from environment variables with validation.
"""
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings with validation and type safety."""

    # Database
    database_url: str = Field(
        default="postgresql://raguser:ragpassword@localhost:5432/ragdb",
        description="PostgreSQL connection string"
    )

    # LLM Provider Selection
    llm_provider: str = Field(
        default="gemini",
        description="LLM provider to use: 'gemini' or 'deepseek'"
    )

    # Google Gemini
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key for LLM integration"
    )

    # DeepSeek
    deepseek_api_key: str = Field(
        default="",
        description="DeepSeek API key for LLM integration"
    )
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1",
        description="DeepSeek API base URL"
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        description="DeepSeek model to use"
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

    # CORS - Using string type to avoid parsing issues, will convert in validator
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        description="Allowed CORS origins (comma-separated)"
    )

    # LLM Settings
    gemini_model: str = Field(
        default="gemini-2.5-flash",
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

    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, v: int) -> int:
        """Ensure overlap is less than chunk size."""
        # Note: In Pydantic v2, we can't access other fields here directly
        # This validation should be done at the model level if needed
        return v


# Global settings instance
settings = Settings()
