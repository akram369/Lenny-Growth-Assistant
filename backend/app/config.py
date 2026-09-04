"""
Application Configuration Settings.
Loads configuration from environment variables and .env file.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General App Settings
    ENVIRONMENT: str = "development"
    APP_NAME: str = "The Lenny Growth Assistant"
    APP_PORT: int = 8001
    DEBUG: bool = True

    # Database & Vector Persistence
    # Defaults to PostgreSQL with pgvector, supports SQLite fallback for local test mode
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_assistant"
    SQLITE_FALLBACK_URL: str = "sqlite+aiosqlite:///./lenny_assistant.db"

    # Active LLM Provider ("ollama" or "cloud")
    DEFAULT_LLM_PROVIDER: str = "ollama"

    # Local LLM (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_TIMEOUT_SECONDS: int = 60

    # Cloud LLM (Anthropic / OpenAI / Groq)
    CLOUD_PROVIDER: str = "groq"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # RAG & Vector Embeddings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_SIMILARITY_THRESHOLD: float = 0.35

    # Transcripts & Chunker Settings
    CHUNK_SIZE_TOKENS: int = 600
    CHUNK_OVERLAP_TOKENS: int = 100


settings = Settings()
