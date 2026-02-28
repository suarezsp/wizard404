"""
Sesion y engine de SQLAlchemy.

Soporta SQLite (por defecto) y PostgreSQL. SQLite requiere check_same_thread=False
para FastAPI; PostgreSQL usa pool_pre_ping.
"""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.models import Base

_is_sqlite = settings.database_url.startswith("sqlite")
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


"""Crea las tablas si no existen. Para SQLite, crea el directorio data/."""
def init_db() -> None:
    if _is_sqlite:
        Path(settings.database_url.replace("sqlite:///", "")).parent.mkdir(
            parents=True, exist_ok=True
        )
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
