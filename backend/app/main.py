"""
Main FastAPI application entry point.
Configures CORS, logging, and initializes services.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, check_db_connection
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting RAG application...")

    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()

        # Check database connection
        if not check_db_connection():
            logger.error("Database connection failed!")
            raise Exception("Database connection failed")

        # Initialize embedding service (lazy loading)
        from app.services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()
        logger.info(f"Embedding service initialized (dimension: {embedding_service.get_dimension()})")

        # Check LLM service
        from app.services.llm_service import get_llm_service
        try:
            llm_service = get_llm_service()
            if llm_service.check_api_status():
                logger.info("LLM service initialized successfully")
            else:
                logger.warning("LLM service may not be working properly")
        except Exception as e:
            logger.warning(f"LLM service initialization warning: {e}")

        logger.info("Application started successfully!")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down RAG application...")


# Create FastAPI application
app = FastAPI(
    title="Simple RAG System",
    description="A Retrieval Augmented Generation system for document Q&A",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["RAG"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Simple RAG System",
        "version": "1.0.0",
        "description": "Retrieval Augmented Generation system for document Q&A",
        "endpoints": {
            "health": "/api/v1/health",
            "upload": "/api/v1/upload",
            "ask": "/api/v1/ask",
            "documents": "/api/v1/documents"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    Ensures proper error responses and logging.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
