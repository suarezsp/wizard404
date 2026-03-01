#!/usr/bin/env python3
"""
Borra todos los documentos del índice y los archivos en el storage.

Deja la base de datos y los usuarios intactos (admin, w404, etc.).
Útil para dejar todo limpio antes de una demo y volver a importar con ./w404 index.

Ejecutar desde la raíz del repo o desde backend/:
  cd backend && python -m scripts.clear_documents

O con el venv:
  cd backend && ./venv/bin/python -m scripts.clear_documents
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.db.models import Document
from app.db.session import SessionLocal, init_db

init_db()
db = SessionLocal()
count = db.query(Document).count()
db.query(Document).delete()
db.commit()
db.close()
print(f"Deleted {count} document(s) from the database.")

# Vaciar la carpeta de storage (archivos copiados al importar)
storage = settings.documents_storage_path
if storage.exists() and storage.is_dir():
    removed = 0
    for f in storage.iterdir():
        if f.is_file():
            try:
                f.unlink()
                removed += 1
            except OSError:
                pass
    print(f"Removed {removed} file(s) from {storage}.")
else:
    print(f"Storage path {storage} does not exist or is not a directory (nothing to clean).")

print("Done. You can re-import with ./w404 index <path> or from the web app.")
