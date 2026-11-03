
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Database connection URL from application settings
DATABASE_URL = settings.DATABASE_URL


# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 5,
    },
)


# Create database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# FastAPI dependency for database sessions
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
