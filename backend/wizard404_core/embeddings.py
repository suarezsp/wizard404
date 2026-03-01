"""
Embeddings para búsqueda semántica con sentence-transformers/all-MiniLM-L6-v2.

Carga lazy del modelo; encode de texto a vector 384-dim; similitud coseno.
Usado por el servicio de documentos cuando semantic=True y hay embeddings en DB.
Si sentence_transformers no está instalado, encode/get_model devuelven None o fallan
y la capa superior hace fallback a expansión de consulta.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from wizard404_core.models import DocumentMetadata, SearchFilters, SearchResult

_MODEL_CACHE: object = None
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_EMBEDDING_DIM = 384

# Truncar texto muy largo (modelo ~512 tokens; ~2000 chars es seguro)
_MAX_TEXT_LEN = 8000


def _get_model():
    """Carga el modelo solo al primer uso (lazy). Devuelve el modelo o None si no está la lib."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    try:
        from sentence_transformers import SentenceTransformer
        _MODEL_CACHE = SentenceTransformer(_MODEL_NAME)
        return _MODEL_CACHE
    except ImportError:
        return None


def get_model():
    """Devuelve el modelo cacheado o None si sentence_transformers no está instalado."""
    return _get_model()


def encode(text: str) -> list[float] | None:
    """
    Convierte texto en vector de 384 dimensiones.
    Devuelve None si la librería no está, el texto está vacío tras normalizar,
    o si model.encode/tolist lanza (OOM, red, etc.); en ese caso se hace fallback.
    """
    model = _get_model()
    if model is None:
        return None
    t = (text or "").strip()
    if not t:
        return None
    if len(t) > _MAX_TEXT_LEN:
        t = t[:_MAX_TEXT_LEN]
    try:
        vec = model.encode(t, convert_to_numpy=True)
        return vec.tolist()
    except Exception as e:
        logger.warning("encode failed: %s", e)
        return None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Similitud coseno entre dos vectores. Pure Python/numpy; no expone torch."""
    if len(a) != len(b) or len(a) == 0:
        return 0.0
    try:
        import numpy as np
        va = np.array(a, dtype=float)
        vb = np.array(b, dtype=float)
        n = np.linalg.norm(va) * np.linalg.norm(vb)
        if n == 0:
            return 0.0
        return float(np.dot(va, vb) / n)
    except ImportError:
        # Fallback sin numpy
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(y * y for y in b) ** 0.5
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)


def embedding_from_json(s: str | None) -> list[float] | None:
    """Deserializa un embedding guardado como JSON. Devuelve None si s es None o inválido."""
    if not s:
        return None
    try:
        out = json.loads(s)
        if isinstance(out, list) and len(out) == _EMBEDDING_DIM and all(isinstance(x, (int, float)) for x in out):
            return [float(x) for x in out]
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def search_by_embeddings(
    documents: list[tuple[DocumentMetadata, list[float]]],
    query: str,
    filters: SearchFilters,
) -> tuple[list[SearchResult], bool]:
    """
    Búsqueda por similitud de embeddings. Filtra por filters (sin query), ordena por score, pagina.
    documents: lista de (DocumentMetadata, embedding).
    query: texto de búsqueda; se codifica y se compara con cada embedding.
    Returns: (results, used_vectors). used_vectors=True si la query se embeddeo y se ordeno por similitud.
    """
    from wizard404_core.models import SearchResult, SearchFilters as SF
    from wizard404_core.search import _apply_filters, _sort_results

    query_stripped = (query or "").strip()
    # Filtros sin query para no filtrar por texto
    filters_no_query = SF(
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
    metas = [meta for meta, _ in documents]
    filtered_metas = _apply_filters(metas, filters_no_query)
    # Mantener (meta, emb) solo para los filtrados
    meta_to_emb = {id(m): emb for m, emb in documents}
    filtered_docs = [(m, meta_to_emb[id(m)]) for m in filtered_metas]

    if not query_stripped:
        # Sin query: ordenar por order_by
        results = [
            SearchResult(metadata=m, snippet=(m.content_preview or "")[:300] or "", score=0.0, id=i)
            for i, (m, _) in enumerate(filtered_docs)
        ]
        results = _sort_results(results, filters.order_by, filters.order_desc)
        start = filters.offset
        end = start + filters.limit
        return (results[start:end], False)

    query_emb = encode(query_stripped)
    if query_emb is None:
        # Fallback: orden por fecha; la query no afecta al orden (modelo no disponible o error)
        logger.warning(
            "search_by_embeddings: query no vacia pero encode devolvio None; orden por order_by (sin similitud)"
        )
        results = [
            SearchResult(metadata=m, snippet=(m.content_preview or "")[:300] or "", score=0.0, id=i)
            for i, (m, _) in enumerate(filtered_docs)
        ]
        results = _sort_results(results, filters.order_by, filters.order_desc)
        start = filters.offset
        end = start + filters.limit
        return (results[start:end], False)

    results = []
    for i, (meta, emb) in enumerate(filtered_docs):
        score = cosine_similarity(query_emb, emb)
        snippet = (meta.content_preview or "")[:300]
        if snippet:
            snippet = "..." + snippet + "..." if len(meta.content_preview or "") > 300 else snippet
        results.append(SearchResult(metadata=meta, snippet=snippet, score=score, id=i))

    def _key(r: SearchResult) -> tuple[float, float, str]:
        dt = (r.metadata.modified_at or r.metadata.created_at) if r.metadata else None
        ts = dt.timestamp() if dt else 0.0
        return (r.score, ts, (r.metadata.name if r.metadata else ""))
    results.sort(key=_key, reverse=True)
    start = filters.offset
    end = start + filters.limit
    return (results[start:end], True)
