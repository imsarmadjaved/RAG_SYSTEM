from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "RAG_Resume_System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str
    WORKERS: int = 4
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "rag_resume_system"
    PINECONE_API_KEY: str
    PINECONE_INDEX_CHUNKS: str = "resume-chunks"
    PINECONE_INDEX_SKILLS: str = "skill-vectors"
    OPENAI_API_KEY: str
    OPENAI_MODEL_CHAT: str = "gpt-4o"
    OPENAI_MODEL_EXTRACTION: str = "gpt-3.5-turbo"
    OPENAI_MODEL_EMBEDDING: str = "text-embedding-3-small"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.3
    REDIS_URL: Optional[str] = None
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAX_PDF_SIZE_MB: int = 10
    PDF_CHUNK_SIZE: int = 500
    PDF_CHUNK_OVERLAP: int = 50
    PDF_EXTRACTION_CONFIDENCE_THRESHOLD: float = 0.7
    RATE_LIMIT_PER_MINUTE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
