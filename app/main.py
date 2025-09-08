from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .middleware import LoggingMiddleware, error_handling_middleware
from .exceptions import register_exception_handlers
from .routers import auth, recipes
from .database import Base, engine
from .core.config import settings

# Create DB tables (for demo; in production use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Powered Cooking Assistant API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
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
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
