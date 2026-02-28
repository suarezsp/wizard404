"""
Servicio de documentos.

Orquesta wizard404_core (extraer y hacer discovery) con la persistencia en PostgreSQL.
"""

import shutil
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Document, User
from wizard404_core import (
    discover_and_extract,
    extract_metadata,
    list_documents,
    search_documents,
)
from wizard404_core.models import DocumentMetadata, SearchFilters, SearchResult


def _doc_to_metadata(doc: Document) -> DocumentMetadata:
    return DocumentMetadata(
        path=doc.path,
        name=doc.name,
        mime_type=doc.mime_type,
        size_bytes=doc.size_bytes,
        created_at=doc.created_at,
        modified_at=doc.modified_at,
        content_preview=doc.content_preview,
        content_full=doc.content_full,
    )


"""
Importa un documento: copia al storage, extrae metadatos y persiste.
"""
def import_document(
    source_path: str | Path,
    user_id: int,
    db: Session,
) -> Document:
    source = Path(source_path).resolve()
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"File not found: {source}")
    meta = extract_metadata(source)
    if not meta:
        raise ValueError(f"Unsupported format: {source.suffix}")
    storage = settings.documents_storage_path
    storage.mkdir(parents=True, exist_ok=True)
    dest_name = f"{source.stem}_{source.stat().st_mtime:.0f}{source.suffix}"
    dest = storage / dest_name
    shutil.copy2(source, dest)
    doc = Document(
        owner_id=user_id,
        path=str(dest),
        name=meta.name,
        mime_type=meta.mime_type,
        size_bytes=meta.size_bytes,
        created_at=meta.created_at,
        modified_at=meta.modified_at,
        content_preview=meta.content_preview,
        content_full=meta.content_full,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


"""Importa todos los documentos soportados de un directorio"""
def import_directory(
    source_path: str | Path,
    user_id: int,
    db: Session,
) -> list[Document]:
    imported = []
    for meta in discover_and_extract(source_path):
        try:
            doc = import_document(meta.path, user_id, db)
            imported.append(doc)
        except (ValueError, FileNotFoundError):
            continue
    return imported

"""Busca documentos del usuario aplicando filtros."""
def search(
    db: Session,
    user_id: int,
    filters: SearchFilters,
) -> list[SearchResult]:
    docs = (
        db.query(Document)
        .filter(Document.owner_id == user_id)
        .all()
    )
    path_to_id = {d.path: d.id for d in docs}
    metas = [_doc_to_metadata(d) for d in docs]
    results = search_documents(metas, filters)
    for r in results:
        if r.metadata:
            r.id = path_to_id.get(r.metadata.path)
    return results


def get_document(db: Session, doc_id: int, user_id: int) -> Document | None:
    return (
        db.query(Document)
        .filter(Document.id == doc_id, Document.owner_id == user_id)
        .first()
    )
