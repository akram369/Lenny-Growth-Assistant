"""
FastAPI Application Entry Point.
Initializes lifespan handlers, CORS middleware, API router, and global exception handlers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import logger
from app.db.session import init_db
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan handler."""
    logger.info(f"Starting {settings.APP_NAME} in [{settings.ENVIRONMENT}] mode...")
    # Initialize database tables and pgvector extension
    db_ok = await init_db()
    if db_ok:
        logger.info("Database initialized and ready.")
    else:
        logger.warning("Database initialization encountered warnings. Check database connectivity.")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Grounded AI conversational assistant for Lenny's Podcast with Ship 30 for 30 essay engine and side-by-side sandboxed artifact rendering.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local frontend development (ports 3000, 5173, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach API Router
app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler ensuring all unhandled exceptions return structured JSON."""
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_type": exc.__class__.__name__,
            "message": "An internal server error occurred.",
            "detail": str(exc) if settings.DEBUG else "Internal server error",
        },
    )


@app.get("/")
async def root():
    """Root status endpoint providing service overview and documentation links."""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "health_check": "/api/health",
    }
