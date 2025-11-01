from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .middleware import LoggingMiddleware, error_handling_middleware
from .exceptions import register_exception_handlers
from .routers import auth, recipes, chat, feedbacks, cooking_sessions, saved_recipes, recommendations, user_preferences, users
from .database import Base, engine
from .core.config import settings

# Create DB tables (for demo; in production use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Powered Cooking Assistant API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ALLOW_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Global error-catching middleware
app.middleware("http")(error_handling_middleware)

# Exception handlers (including Pydantic validation errors)
register_exception_handlers(app)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(user_preferences.router, prefix="/preferences", tags=["preferences"])
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(feedbacks.router, prefix="/feedbacks", tags=["feedbacks"])
app.include_router(cooking_sessions.router, prefix="/cooking-sessions", tags=["cooking-sessions"])
app.include_router(saved_recipes.router, prefix="/saved-recipes", tags=["saved-recipes"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
