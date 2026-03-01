"""
Sesion y engine de SQLAlchemy.

Soporta SQLite (por defecto) y PostgreSQL. SQLite requiere check_same_thread=False
para FastAPI; PostgreSQL usa pool_pre_ping.
"""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, text
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


"""Crea las tablas si no existen. Para SQLite, crea el directorio data/. Anade columnas author/title a documents si faltan (migracion suave)."""
def init_db() -> None:
    if _is_sqlite:
        Path(settings.database_url.replace("sqlite:///", "")).parent.mkdir(
            parents=True, exist_ok=True
        )
    Base.metadata.create_all(bind=engine)
    # Migracion suave: anadir columnas a documents si la tabla ya existia sin ellas
    with engine.connect() as conn:
        for col, sql_type in (("author", "VARCHAR(512)"), ("title", "VARCHAR(512)"), ("embedding", "TEXT")):
            try:
                conn.execute(text(f"ALTER TABLE documents ADD COLUMN {col} {sql_type}"))
                conn.commit()
            except Exception:
                conn.rollback()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
