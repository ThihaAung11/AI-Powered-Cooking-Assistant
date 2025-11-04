from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .middleware import LoggingMiddleware, error_handling_middleware
from .exceptions import register_exception_handlers
from .routers import auth, recipes, chat, feedbacks, cooking_sessions, saved_recipes, recommendations, user_preferences, users, collections, shopping_lists
from .database import Base, engine
from .core.config import settings

# Create DB tables (for demo; in production use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Powered Cooking Assistant API", version="1.0.0")

# CORS
if settings.CORS_ALLOW_ORIGINS.strip() == "*":
    _cors_origins = ["*"]
    _cors_allow_credentials = False  # Starlette forbids credentials with wildcard origin
else:
    _cors_origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()]
    _cors_allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_allow_credentials,
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
app.include_router(collections.router, prefix="/collections", tags=["collections"])
app.include_router(shopping_lists.router, prefix="/shopping-lists", tags=["shopping-lists"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
