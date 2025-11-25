from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

from .core.config import settings

from datetime import datetime, timezone

DATABASE_URL = settings.DATABASE_URL

# SQLite needs check_same_thread=False
# For PostgreSQL, configure connection pooling to avoid max connections error
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL/Supabase configuration with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,          # Number of connections to maintain in the pool
        max_overflow=10,      # Maximum additional connections beyond pool_size
        pool_pre_ping=True,   # Validate connections before use
        pool_recycle=3600,    # Recycle connections after 1 hour
        echo=False            # Set to True for SQL debugging
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CommonModel(Base):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

