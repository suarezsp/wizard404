"""
Busqueda y listado de documentos.

Funciones puras que operan sobre listas de DocumentMetadata.
La persistencia real se delega a la capa de infraestructura (DB).
-> logica de filtrado y ordenacion.
"""

import fnmatch
from datetime import datetime

from wizard404_core.models import DocumentMetadata, SearchFilters, SearchResult


def search_documents(
    documents: list[DocumentMetadata],
    filters: SearchFilters,
) -> list[SearchResult]:
    """
    Filtra y ordena documentos segun SearchFilters.
    Busqueda por palabras clave en nombre y content_preview; devuelve resultados paginados con snippet y score.
    Si hay query, ordena por relevancia (score) y luego por fecha; si no, usa filters.order_by y order_desc.
    """
    filtered = _apply_filters(documents, filters)
    query_stripped = filters.query.strip() if filters.query else ""
    results = []
    for i, doc in enumerate(filtered):
        snippet = ""
        score = 0.0
        if query_stripped:
            snippet, score = _compute_snippet_and_score(doc, filters.query)
        results.append(
            SearchResult(metadata=doc, snippet=snippet, score=score, id=i)
        )
    if query_stripped:
        # Orden por relevancia (score) y luego por fecha (más reciente primero)
        def _relevance_key(r: SearchResult) -> tuple[float, float, str]:
            doc = r.metadata
            dt = (doc.modified_at or doc.created_at) if doc else None
            ts = dt.timestamp() if dt else 0.0
            return (r.score, ts, (doc.name if doc else ""))
        results.sort(key=_relevance_key, reverse=True)
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

def list_documents(
    documents: list[DocumentMetadata],
    filters: SearchFilters,
) -> list[SearchResult]:
    """Lista documentos con filtros (sin búsqueda por texto). Útil para browse y listados paginados."""
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
        tokens = _tokenize_query(f.query)
        if tokens:
            result = [
                d for d in result
                if any(
                    t in d.name.lower() or t in (d.content_preview or "").lower()
                    for t in tokens
                )
            ]
    return result


def _tokenize_query(query: str) -> list[str]:
    """Split query into non-empty tokens (lowercase)."""
    return [t for t in query.lower().split() if t]


"""Genera snippet y score de relevancia para la busqueda (multi-palabra)."""
def _compute_snippet_and_score(doc: DocumentMetadata, query: str) -> tuple[str, float]:
    tokens = _tokenize_query(query)
    if not tokens:
        return "", 0.0

    name_lower = doc.name.lower()
    preview_lower = (doc.content_preview or "").lower()
    score = 0.0
    for t in tokens:
        if t in name_lower:
            score += 10.0
        if t in preview_lower:
            score += 5.0

    # Optional bonus: doc contains all query tokens
    if all(t in name_lower or t in preview_lower for t in tokens):
        score += 2.0

    # Snippet: longer context (±80) around first matching token for readability
    snippet = ""
    for t in tokens:
        idx = preview_lower.find(t)
        if idx >= 0:
            start = max(0, idx - 80)
            end = min(len(doc.content_preview), idx + len(t) + 80)
            snippet = "..." + doc.content_preview[start:end] + "..."
            break
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
