import os
from typing import Optional, List


class Settings:
    DATABASE_URL: str = "sqlite:///./decisionmate.db"
    CORS_ORIGINS: List[str] = ["*"]
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    SERP_API_KEY: Optional[str] = os.getenv("SERP_API_KEY")
    DEBUG: bool = True


settings = Settings()
