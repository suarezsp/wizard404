"""
Endpoints de los documentos

-> CRUD, importar, buscar, explorar + ver detalles
"""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.services.documents import (
    get_document,
    import_document,
    import_directory,
    search,
)
from wizard404_core.models import SearchFilters

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    path: str
    mime_type: str
    size_bytes: int
    content_preview: str


class SearchResponse(BaseModel):
    id: int | None
    name: str
    path: str
    mime_type: str
    size_bytes: int
    snippet: str


@router.get("/search", response_model=list[SearchResponse])
def search_docs(
    q: Annotated[str, Query(description="Keywords to search")] = "",
    mime_type: str | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = SearchFilters(
        query=q,
        mime_type=mime_type,
        min_size=min_size,
        max_size=max_size,
        limit=limit,
        offset=offset,
    )
    results = search(db, current_user.id, filters)
    return [
        SearchResponse(
            id=r.id,
            name=r.metadata.name if r.metadata else "",
            path=r.metadata.path if r.metadata else "",
            mime_type=r.metadata.mime_type if r.metadata else "",
            size_bytes=r.metadata.size_bytes if r.metadata else 0,
            snippet=r.snippet,
        )
        for r in results if r.metadata
    ]


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_doc(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
    )

"""Importar un archivo/directorio desde el path del sistema"""
@router.post("/import")
def import_path(
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    try:
        p = Path(path)
        if p.is_file():
            doc = import_document(p, current_user.id, db)
            return {"imported": 1, "document_id": doc.id}
        if p.is_dir():
            docs = import_directory(p, current_user.id, db)
            return {"imported": len(docs), "document_ids": [d.id for d in docs]}
        raise HTTPException(status_code=400, detail="Invalid path")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) # wizard 404! 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
