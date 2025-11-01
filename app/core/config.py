import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    app_name: str = "AI-Powered Cooking Assistant API"
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    # Default SQLite
    DATABASE_URL: str 
    # Example for PostgreSQL:
    # DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/yourdb

    # CORS (comma-separated)
    CORS_ALLOW_ORIGINS: str = "*"

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-5-mini"
    OPENAI_TEMPERATURE: float = 0.6

    class Config:
        env_file = ".env"
        allow_extra = True
        env_file_encoding = "utf-8"

settings = Settings()
print(settings.DATABASE_URL)
