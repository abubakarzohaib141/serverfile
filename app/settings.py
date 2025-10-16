from pydantic import BaseModel
import os

class Settings(BaseModel):
    APP_NAME: str = "ABZ Agent API"
    ENV: str = os.getenv("ENV", "dev")
    CORS_ALLOW_ORIGINS: list[str] = [
        os.getenv("NEXT_PUBLIC_SITE_URL", "http://localhost:3000"),
        "http://localhost:3000",
    ]
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "false"
    # When you add your real agent, you may want e.g. GEMINI_API_KEY from env.

settings = Settings()
