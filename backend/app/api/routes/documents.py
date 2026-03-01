"""
Endpoints de documentos: listar, buscar, importar, subir, ver detalle y resumen.
CRUD + explorar indice; auth requerida en list/search.
"""

import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.path_utils import validate_local_path
from app.core.config import settings
from app.db.models import User
from app.db.session import get_db
from app.services.documents import (
    get_document,
    import_document,
    import_directory,
    list_documents_by_owner,
    reindex_embeddings,
    search,
    assist_from_documents,
)
from wizard404_core.extractors.image import _suppress_stderr_fd
from wizard404_core.models import SearchFilters
from wizard404_core.summary import summarize_text

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_PATH_LEN = 4096


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    path: str
    mime_type: str
    size_bytes: int
    content_preview: str
    author: str | None = None
    title: str | None = None


class SearchResponse(BaseModel):
    id: int | None
    name: str
    path: str
    mime_type: str
    size_bytes: int
    snippet: str


class AssistRequest(BaseModel):
    """Cuerpo para POST /documents/assist: documentos de contexto e identificadores de huecos."""
    context_doc_ids: list[int] = []
    placeholders: list[str] = []


class AssistResponse(BaseModel):
    suggestions: dict[str, str]


@router.get("", response_model=list[SearchResponse])
def list_docs(
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista documentos indexados del usuario con paginacion (limit/offset). Orden: mas recientes primero (imported_at desc)."""
    limit = min(max(1, limit), settings.max_list_limit)
    offset = max(0, offset)
    docs = list_documents_by_owner(db, current_user.id, limit=limit, offset=offset)
    return [
        SearchResponse(
            id=d.id,
            name=d.name,
            path=d.path,
            mime_type=d.mime_type,
            size_bytes=d.size_bytes,
            snippet=d.content_preview[:500] if d.content_preview else "",
        )
        for d in docs
    ]


@router.get("/search")
def search_docs(
    q: Annotated[str, Query(description="Keywords to search")] = "",
    semantic: bool = False,
    mime_type: str | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
    order_by: str = "modified_at",
    order_desc: bool = True,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Busca en documentos indexados del usuario. q vacio devuelve lista vacia. semantic=true usa expansion de consulta o vectores. Header X-Semantic-Used indica si se ordeno por similitud."""
    limit = min(max(1, limit), settings.max_search_limit)
    offset = max(0, offset)
    filters = SearchFilters(
        query=q,
        mime_type=mime_type,
        min_size=min_size,
        max_size=max_size,
        order_by=order_by,
        order_desc=order_desc,
        limit=limit,
        offset=offset,
    )
    results, semantic_used = search(db, current_user.id, filters, semantic=semantic)
    body = [
        {
            "id": r.id,
            "name": r.metadata.name if r.metadata else "",
            "path": r.metadata.path if r.metadata else "",
            "mime_type": r.metadata.mime_type if r.metadata else "",
            "size_bytes": r.metadata.size_bytes if r.metadata else 0,
            "snippet": r.snippet,
        }
        for r in results if r.metadata
    ]
    return JSONResponse(
        content=body,
        headers={"X-Semantic-Used": "true" if semantic_used else "false"},
    )


@router.post("/reindex-embeddings")
def reindex_embeddings_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recalcula embeddings para todos los documentos del usuario. Util si la busqueda semantica no varia con la consulta (documentos importados antes del texto rico)."""
    n = reindex_embeddings(db, current_user.id)
    return {"reindexed": n}


@router.get("/{doc_id}/summary")
def get_doc_summary(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve un resumen automático del documento (extractivo, primeras frases)."""
    doc = get_document(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    content = (doc.content_full or doc.content_preview or "").strip()
    summary = summarize_text(content, max_chars=300)
    return {"summary": summary, "doc_id": doc_id}


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve un documento indexado por id. 404 si no existe o no pertenece al usuario."""
    doc = get_document(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(
        id=doc.id,
        name=doc.name,
        path=doc.path,
        mime_type=doc.mime_type,
        size_bytes=doc.size_bytes,
        content_preview=doc.content_preview,
        author=doc.author,
        title=doc.title,
    )

@router.post("/import")
def import_path(
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Importa un archivo o directorio desde el path del sistema al índice del usuario (copia a storage y persiste en DB)."""
    try:
        p = validate_local_path(path, max_len=MAX_PATH_LEN)
        if p.is_file():
            if p.stat().st_size > settings.max_import_file_bytes:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large (max {settings.max_import_file_bytes // (1024*1024)} MB)",
                )
            with _suppress_stderr_fd():
                doc = import_document(p, current_user.id, db)
            return {"imported": 1, "document_id": doc.id}
        if p.is_dir():
            with _suppress_stderr_fd():
                docs = import_directory(p, current_user.id, db)
            return {"imported": len(docs), "document_ids": [d.id for d in docs]}
        raise HTTPException(status_code=400, detail="Invalid path")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OSError as e:
        raise HTTPException(status_code=503, detail=f"Storage or filesystem error: {e}")


@router.post("/upload")
def upload_documents(
    files: Annotated[list[UploadFile], File(description="Files to import")],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Importa archivos subidos (multipart). Para cada archivo: guarda en temp,
    reutiliza import_document, borra temp. Limite de tamano y cantidad por request.
    """
    if len(files) > settings.max_upload_files_per_request:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files (max {settings.max_upload_files_per_request})",
        )
    imported_ids: list[int] = []
    for upload in files:
        if not upload.filename or upload.filename.strip() == "":
            continue
        suffix = Path(upload.filename).suffix or ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = upload.file.read()
                if len(content) > settings.max_import_file_bytes:
                    continue
                tmp.write(content)
                tmp_path = Path(tmp.name)
            try:
                with _suppress_stderr_fd():
                    doc = import_document(tmp_path, current_user.id, db)
                imported_ids.append(doc.id)
            finally:
                tmp_path.unlink(missing_ok=True)
        except (ValueError, FileNotFoundError, OSError):
            continue
    return {"imported": len(imported_ids), "document_ids": imported_ids}


@router.post("/assist", response_model=AssistResponse)
def assist(
    body: AssistRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sugerencias para completar plantilla a partir de documentos de contexto (asistente)."""
    suggestions = assist_from_documents(
        db, current_user.id, body.context_doc_ids, body.placeholders
    )
    return AssistResponse(suggestions=suggestions)
