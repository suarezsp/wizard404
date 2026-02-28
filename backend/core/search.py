"""
Busqueda y listado de documentos.

Funciones puras que operan sobre listas de DocumentMetadata.
La persistencia real se delega a la capa de infraestructura (DB).
-> logica de filtrado y ordenacion.
"""

import fnmatch
from datetime import datetime

from wizard404_core.models import DocumentMetadata, SearchFilters, SearchResult


"""
Filtra y ordena documentos segun SearchFilters.
Busqueda por palabras clave en nombre y content_preview.
"""
def search_documents(
    documents: list[DocumentMetadata],
    filters: SearchFilters,
) -> list[SearchResult]:
    filtered = _apply_filters(documents, filters)
    query_lower = filters.query.lower().strip()
    results = []
    for i, doc in enumerate(filtered):
        snippet = ""
        score = 0.0
        if query_lower:
            snippet, score = _compute_snippet_and_score(doc, query_lower)
        results.append(
            SearchResult(metadata=doc, snippet=snippet, score=score, id=i)
        )
    if query_lower:
        results.sort(key=lambda r: r.score, reverse=True)
    else:
        results = _sort_results(
            [r for r in results],
            filters.order_by,
            filters.order_desc,
        )
    # Paginacion
    start = filters.offset
    end = start + filters.limit
    return results[start:end]

"""Lista documentos con filtros (sin busqueda por texto).
Util para browse y listados paginados.
"""
def list_documents(
    documents: list[DocumentMetadata],
    filters: SearchFilters,
) -> list[SearchResult]:
    filters = SearchFilters(
        query="",
        mime_type=filters.mime_type,
        min_size=filters.min_size,
        max_size=filters.max_size,
        from_date=filters.from_date,
        to_date=filters.to_date,
        directory=filters.directory,
        limit=filters.limit,
        offset=filters.offset,
        order_by=filters.order_by,
        order_desc=filters.order_desc,
        name_pattern=filters.name_pattern,
        date_field=filters.date_field,
        name_contains=filters.name_contains,
    )
    return search_documents(documents, filters)


"""Filtra una lista de DocumentMetadata segun SearchFilters. Publico para uso en CLI/import."""
def apply_filters(
    docs: list[DocumentMetadata],
    f: SearchFilters,
) -> list[DocumentMetadata]:
    return _apply_filters(docs, f)

"""Filtra una lista de DocumentMetadata segun SearchFilters."""
def _apply_filters(
    docs: list[DocumentMetadata],
    f: SearchFilters,
) -> list[DocumentMetadata]:
    result = list(docs)
    if f.mime_type:
        result = [d for d in result if d.mime_type == f.mime_type]
    if f.min_size is not None:
        result = [d for d in result if d.size_bytes >= f.min_size]
    if f.max_size is not None:
        result = [d for d in result if d.size_bytes <= f.max_size]
    date_attr = f.date_field if f.date_field in ("modified_at", "created_at") else "modified_at"
    if f.from_date:
        result = [
            d for d in result
            if getattr(d, date_attr) and getattr(d, date_attr) >= f.from_date
        ]
    if f.to_date:
        result = [
            d for d in result
            if getattr(d, date_attr) and getattr(d, date_attr) <= f.to_date
        ]
    if f.directory:
        dir_norm = f.directory.rstrip("/")
        result = [d for d in result if dir_norm in d.path]
    if f.name_pattern:
        result = [d for d in result if fnmatch.fnmatch(d.name, f.name_pattern)]
    if f.name_contains:
        sub = f.name_contains.lower()
        result = [d for d in result if sub in d.name.lower()]
    if f.query:
        q = f.query.lower()
        result = [
            d for d in result
            if q in d.name.lower() or q in d.content_preview.lower()
        ]
    return result


"""Genera snippet y score de relevancia para la busqueda."""
def _compute_snippet_and_score(doc: DocumentMetadata, query: str) -> tuple[str, float]:
    score = 0.0
    if query in doc.name.lower():
        score += 10.0
    if query in doc.content_preview.lower():
        score += 5.0
    # Snippet: primera ocurrencia con contexto
    snippet = ""
    if query in doc.content_preview.lower():
        idx = doc.content_preview.lower().find(query)
        start = max(0, idx - 50)
        end = min(len(doc.content_preview), idx + len(query) + 50)
        snippet = "..." + doc.content_preview[start:end] + "..."
    return snippet, score


def _sort_results(
    results: list[SearchResult],
    order_by: str,
    desc: bool,
) -> list[SearchResult]:
    def key_fn(r: SearchResult):
        doc = r.metadata
        if not doc:
            return (0, "")
        fallback_dt = datetime.min
        if order_by == "modified_at":
            dt = doc.modified_at or doc.created_at
            return (dt or fallback_dt, doc.name)
        if order_by == "created_at":
            dt = doc.created_at or doc.modified_at
            return (dt or fallback_dt, doc.name)
        if order_by == "size":
            return (doc.size_bytes, doc.name)
        if order_by == "name":
            return (doc.name.lower(), doc.path)
        dt = doc.modified_at or doc.created_at
        return (dt or fallback_dt, doc.name)

    return sorted(results, key=key_fn, reverse=desc)
