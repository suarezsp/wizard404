"""
Servicio de documentos.

Orquesta wizard404_core (extraer y hacer discovery) con la persistencia en PostgreSQL.
"""

import json
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
    semantic_search_documents,
    search_by_embeddings,
    encode_embedding,
    embedding_from_json,
)
from wizard404_core.models import DocumentMetadata, SearchFilters, SearchResult

# Max caracteres para el texto que se embedea (coherente con wizard404_core.embeddings)
_EMBED_TEXT_MAX_LEN = 8000
_CONTENT_FULL_PREFIX = 2500


def _text_for_embedding(meta: DocumentMetadata) -> str:
    """
    Texto rico para calcular el embedding: titulo, nombre, preview y prefijo de content_full.
    Asi documentos con contenido distinto reciben embeddings diferenciados.
    """
    parts = [
        (meta.title or "").strip(),
        (meta.name or "").strip(),
        (meta.content_preview or "").strip(),
        ((meta.content_full or "")[:_CONTENT_FULL_PREFIX]).strip(),
    ]
    combined = " ".join(p for p in parts if p)
    return combined[:_EMBED_TEXT_MAX_LEN].strip() or meta.name or ""


def _doc_to_metadata(doc: Document) -> DocumentMetadata:
    """Convierte un modelo Document de DB a DocumentMetadata del core."""
    return DocumentMetadata(
        path=doc.path,
        name=doc.name,
        mime_type=doc.mime_type,
        size_bytes=doc.size_bytes,
        created_at=doc.created_at,
        modified_at=doc.modified_at,
        content_preview=doc.content_preview,
        content_full=doc.content_full,
        author=doc.author,
        title=doc.title,
    )


def import_document(
    source_path: str | Path,
    user_id: int,
    db: Session,
) -> Document:
    """
    Importa un documento: copia al storage, extrae metadatos y persiste en DB.
    Raises: FileNotFoundError si el archivo no existe; ValueError si el formato no es soportado o el archivo excede el tamaño máximo.
    """
    source = Path(source_path).resolve()
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"File not found: {source}")
    max_bytes = getattr(settings, "max_import_file_bytes", 50 * 1024 * 1024)
    if source.stat().st_size > max_bytes:
        raise ValueError(f"File too large (max {max_bytes // (1024*1024)} MB)")
    meta = extract_metadata(source)
    if not meta:
        raise ValueError(f"Unsupported format: {source.suffix}")
    storage = settings.documents_storage_path
    storage.mkdir(parents=True, exist_ok=True)
    dest_name = f"{source.stem}_{source.stat().st_mtime:.0f}{source.suffix}"
    dest = storage / dest_name
    try:
        shutil.copy2(source, dest)
    except OSError as e:
        raise OSError(f"Failed to copy file to storage: {e}") from e
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
        author=getattr(meta, "author", None),
        title=getattr(meta, "title", None),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    # Embedding para búsqueda semántica (texto rico para diferenciar documentos)
    try:
        text_for_emb = _text_for_embedding(meta)
        emb = encode_embedding(text_for_emb) if text_for_emb else None
        if emb is not None:
            doc.embedding = json.dumps(emb)
            db.commit()
            db.refresh(doc)
    except Exception:
        pass
    return doc


def import_directory(
    source_path: str | Path,
    user_id: int,
    db: Session,
) -> list[Document]:
    """Importa todos los documentos soportados de un directorio. Ignora archivos no soportados o inaccesibles."""
    imported = []
    for meta in discover_and_extract(source_path):
        try:
            doc = import_document(meta.path, user_id, db)
            imported.append(doc)
        except (ValueError, FileNotFoundError, OSError):
            continue
    return imported

def search(
    db: Session,
    user_id: int,
    filters: SearchFilters,
    semantic: bool = False,
) -> tuple[list[SearchResult], bool]:
    """
    Busca documentos del usuario.
    Si semantic=True y hay query: usa búsqueda por embeddings cuando existan embeddings en DB;
    si no hay ninguno, fallback a expansión de consulta. Si semantic=False usa búsqueda por términos.
    Returns: (results, semantic_used). semantic_used=True solo cuando se usaron vectores con query embedeada.
    """
    docs = (
        db.query(Document)
        .filter(Document.owner_id == user_id)
        .all()
    )
    path_to_id = {d.path: d.id for d in docs}
    metas = [_doc_to_metadata(d) for d in docs]

    if semantic and (filters.query or "").strip():
        # Documentos con embedding para búsqueda por vectores
        docs_with_emb = [
            (_doc_to_metadata(d), embedding_from_json(d.embedding))
            for d in docs
            if d.embedding
        ]
        docs_with_emb = [(m, e) for m, e in docs_with_emb if e is not None]
        if docs_with_emb:
            results, used_vectors = search_by_embeddings(docs_with_emb, filters.query, filters)
            for r in results:
                if r.metadata:
                    r.id = path_to_id.get(r.metadata.path)
            return (results, used_vectors)
        # Fallback: ningún documento tiene embedding
    search_fn = semantic_search_documents if semantic else search_documents
    results = search_fn(metas, filters)
    for r in results:
        if r.metadata:
            r.id = path_to_id.get(r.metadata.path)
    return (results, False)


def reindex_embeddings(db: Session, user_id: int) -> int:
    """
    Recalcula embeddings para todos los documentos del usuario usando _text_for_embedding.
    Útil cuando los documentos se importaron antes de tener texto rico para embeddings.
    Returns: número de documentos reindexados (con embedding actualizado).
    """
    docs = (
        db.query(Document)
        .filter(Document.owner_id == user_id)
        .all()
    )
    reindexed = 0
    for doc in docs:
        meta = _doc_to_metadata(doc)
        text_for_emb = _text_for_embedding(meta)
        if not text_for_emb:
            continue
        try:
            emb = encode_embedding(text_for_emb)
            if emb is not None:
                doc.embedding = json.dumps(emb)
                db.commit()
                db.refresh(doc)
                reindexed += 1
        except Exception:
            continue
    return reindexed


def get_document(db: Session, doc_id: int, user_id: int) -> Document | None:
    """Devuelve un documento por id si pertenece al usuario, o None si no existe."""
    return (
        db.query(Document)
        .filter(Document.id == doc_id, Document.owner_id == user_id)
        .first()
    )


def list_documents_by_owner(
    db: Session,
    user_id: int,
    limit: int = 200,
    offset: int = 0,
) -> list[Document]:
    """Lista los documentos del usuario con paginación (limit/offset), ordenados por fecha de importación descendente."""
    return (
        db.query(Document)
        .filter(Document.owner_id == user_id)
        .order_by(Document.imported_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def assist_from_documents(
    db: Session,
    user_id: int,
    context_doc_ids: list[int],
    placeholders: list[str],
) -> dict[str, str]:
    """
    Sugerencias para completar plantilla: extrae texto de los documentos de contexto
    y asigna a cada placeholder un fragmento (p. ej. resumen o primeras líneas).
    """
    from wizard404_core.summary import summarize_text

    suggestions: dict[str, str] = {}
    combined_content: list[str] = []
    for doc_id in context_doc_ids[:10]:  # límite razonable
        doc = get_document(db, doc_id, user_id)
        if doc and (doc.content_preview or doc.content_full):
            combined_content.append((doc.content_full or doc.content_preview or "").strip())
    context_text = "\n\n".join(combined_content) if combined_content else ""
    summary = summarize_text(context_text, max_chars=500)
    for name in placeholders[:20]:
        if name.strip():
            suggestions[name.strip()] = summary
    return suggestions
