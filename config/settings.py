"""
Configuration settings for AI Recruitr
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RESUMES_DIR = DATA_DIR / "resumes"
FAISS_INDEX_DIR = DATA_DIR / "faiss_index"
PROCESSED_DIR = DATA_DIR / "processed"

# Create directories if they don't exist
for dir_path in [DATA_DIR, RESUMES_DIR, FAISS_INDEX_DIR, PROCESSED_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration
class Settings:
    # Gemini LLM Configuration

    RESUMES_DIR: str = DATA_DIR / "resumes"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Embedding Model Configuration
    EMBEDDING_MODEL: str = "mixedbread-ai/mxbai-embed-large-v1"
    EMBEDDING_DIMENSION: int = 1024  # Will be updated based on actual model
    MAX_SEQUENCE_LENGTH: int = 512

    # FAISS Configuration
    FAISS_INDEX_PATH: str = str(FAISS_INDEX_DIR / "resume_index.faiss")
    FAISS_METADATA_PATH: str = str(FAISS_INDEX_DIR / "resume_metadata.json")

    # FastAPI Configuration
    API_HOST: str = "localhost"
    API_PORT: int = 8003
    API_RELOAD: bool = True

    # Streamlit Configuration
    STREAMLIT_HOST: str = "localhost"
    STREAMLIT_PORT: int = 8501

    # Resume Processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt"]

    # Matching Configuration
    TOP_K_MATCHES: int = 10
    SIMILARITY_THRESHOLD: float = 0.7

    # Cache Configuration
    ENABLE_CACHE: bool = True
    CACHE_EXPIRY: int = 3600  # 1 hour

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Global settings instance
settings = Settings()

# Validation
def validate_settings():
    """Validate critical settings"""
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is required. Please set it in your .env file")

    print(f"✅ Settings validated successfully")
    print(f"📁 Data directory: {DATA_DIR}")
    print(f"🤖 Embedding model: {settings.EMBEDDING_MODEL}")
    print(f"🧠 Gemini model: {settings.GEMINI_MODEL}")

if __name__ == "__main__":
    validate_settings()