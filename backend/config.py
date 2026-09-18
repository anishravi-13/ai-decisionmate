import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=backend_dir / ".env")
load_dotenv(dotenv_path=backend_dir.parent / ".env")
load_dotenv()


class Settings:
    db_file = (backend_dir / "decisionmate.db").resolve().as_posix()
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{db_file}")
    CORS_ORIGINS: List[str] = ["*"]
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    SERP_API_KEY: Optional[str] = os.getenv("SERP_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    DEBUG: bool = True


settings = Settings()
