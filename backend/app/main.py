"""
Punto de entrada de la API FastAPI.

Monta los routers de auth y documents. Inicializa la base de datos al arrancar.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, documents, scan
from app.core.config import settings
from app.db.session import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager de arranque: inicializa la base de datos; hace yield y cierra al apagar."""
    try:
        init_db()
    except Exception as e:
        logger.exception("Error initializing database: %s", e)
        raise RuntimeError(
            "Error connecting to database. "
            "Check DATABASE_URL and that PostgreSQL is running (or use SQLite by default)."
        ) from e
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(scan.router)


@app.get("/")
def root():
    """Raíz de la API: mensaje de bienvenida y enlace a la documentación interactiva."""
    return {"message": "Wizard404 API", "docs": "/docs"}


@app.get("/health")
def health():
    """Health check para despliegues y CLI. Comprueba conectividad con la base de datos."""
    try:
        from sqlalchemy import text
        from app.db.session import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "database": db_status}
