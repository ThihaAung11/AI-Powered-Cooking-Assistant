import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "AI-Powered Cooking Assistant API"
    secret_key: str = os.getenv("SECRET_KEY", "CHANGE_ME")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    cors_allow_origins: list[str] = (
        os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if os.getenv("CORS_ALLOW_ORIGINS") else ["*"]
    )

settings = Settings()
