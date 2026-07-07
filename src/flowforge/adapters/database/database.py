import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

# Read DATABASE_URL from environment, fallback to SQLite in-memory as agreed
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

# Configure engine with StaticPool for in-memory SQLite to persist connection across session boundaries
if DATABASE_URL.startswith("sqlite"):
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
else:
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True
    )

# Async session maker
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Declarative base class for SQLAlchemy models."""
    pass

async def init_db():
    """Initializes the database tables (used for testing and dev)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
