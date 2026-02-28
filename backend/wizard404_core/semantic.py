"""
Búsqueda semántica ligera: expansión de consulta para mejorar recall.

Sin dependencias de embeddings. Expande la query con variaciones simples
(singular/plural, términos relacionados) para que búsquedas como "contrato"
también encuentren "contracts" o "informe" encuentre "informes".
"""

from wizard404_core.models import DocumentMetadata, SearchFilters, SearchResult


# Pequeño mapa de variaciones para expansión de consulta (es/en, singular/plural).
_QUERY_EXPANSIONS: dict[str, list[str]] = {
    "contract": ["contracts", "contract"],
    "contracts": ["contract", "contracts"],
    "contrato": ["contratos", "contrato"],
    "contratos": ["contrato", "contratos"],
    "informe": ["informes", "informe", "report"],
    "informes": ["informe", "informes", "reports"],
    "report": ["reports", "report", "informe"],
    "reports": ["report", "reports", "informes"],
    "order": ["orders", "order"],
    "orders": ["order", "orders"],
    "pedido": ["pedidos", "pedido"],
    "pedidos": ["pedido", "pedidos"],
}


def expand_query(query: str) -> list[str]:
    """
    Expande la consulta con variaciones (sinónimos, singular/plural).
    Devuelve una lista de términos; al menos incluye el query original en minúsculas.
    """
    q = query.lower().strip()
    if not q:
        return []
    terms = [q]
    # Variación simple: quitar 's' final para plural
    if len(q) > 1 and q.endswith("s") and not q.endswith("ss"):
        base = q[:-1]
        if base not in terms:
            terms.append(base)
    # Añadir singular si la query es plural común
    if q in _QUERY_EXPANSIONS:
        for t in _QUERY_EXPANSIONS[q]:
            if t not in terms:
                terms.append(t)
    return terms


def semantic_search_documents(
    documents: list[DocumentMetadata],
    filters: SearchFilters,
) -> list[SearchResult]:
    """
    Búsqueda que usa expansión de consulta para mejorar recall (modo semántico).
    Filtra por otros criterios (mime_type, size, etc.) y puntúa por coincidencia
    con cualquiera de los términos expandidos.
    """
    from wizard404_core.search import _apply_filters, _sort_results

    query_lower = filters.query.lower().strip()
    terms = expand_query(filters.query) if query_lower else []

    # Aplicar filtros no relacionados con query (mime, size, etc.)
    filters_no_query = SearchFilters(
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
    filtered = _apply_filters(documents, filters_no_query)

    results: list[SearchResult] = []
    for i, doc in enumerate(filtered):
        snippet = ""
        score = 0.0
        if terms:
            name_lower = doc.name.lower()
            preview_lower = doc.content_preview.lower()
            for term in terms:
                if term in name_lower:
                    score += 10.0
                if term in preview_lower:
                    score += 5.0
                    if not snippet:
                        idx = preview_lower.find(term)
                        start = max(0, idx - 50)
                        end = min(len(doc.content_preview), idx + len(term) + 50)
                        snippet = "..." + doc.content_preview[start:end] + "..."
        results.append(SearchResult(metadata=doc, snippet=snippet, score=score, id=i))

    if terms:
        def _relevance_key(r: SearchResult) -> tuple[float, float, str]:
            doc = r.metadata
            dt = (doc.modified_at or doc.created_at) if doc else None
            ts = dt.timestamp() if dt else 0.0
            return (r.score, ts, (doc.name if doc else ""))
        results.sort(key=_relevance_key, reverse=True)
    else:
        results = _sort_results(results, filters.order_by, filters.order_desc)

    start = filters.offset
    end = start + filters.limit
    return results[start:end]
