from pathlib import Path
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "GhostTrace AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    BASE_DIR: Path = BASE_DIR
    DATASET_DIR: Path = BASE_DIR / "dataset"
    EVIDENCE_DIR: Path = DATASET_DIR / "evidence"
    OUTPUT_FILE: Path = BASE_DIR / "output.csv"
    SAMPLE_OUTPUT_FILE: Path = DATASET_DIR / "sample_output.csv"
    DB_PATH: Path = BASE_DIR / "backend" / "db" / "ghosttrace.db"
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 1000
    
    # Audit Engine Settings
    BATCH_SIZE: int = 50
    ALLOW_SYNTHETIC_EVAL: bool = True
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

settings = Settings()
