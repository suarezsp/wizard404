"""
Tests del módulo de embeddings: cosine_similarity, embedding_from_json, encode, search_by_embeddings.
"""

from unittest.mock import patch

import pytest

from wizard404_core.embeddings import (
    cosine_similarity,
    embedding_from_json,
    encode,
    search_by_embeddings,
)
from wizard404_core.models import DocumentMetadata, SearchFilters


def test_cosine_similarity_identical():
    """Vectores idénticos tienen similitud 1.0."""
    v = [0.1, 0.2, 0.3] * 128  # 384 dims
    assert abs(cosine_similarity(v, v) - 1.0) < 1e-6


def test_cosine_similarity_orthogonal():
    """Vectores ortogonales tienen similitud 0."""
    a = [1.0] + [0.0] * 383
    b = [0.0, 1.0] + [0.0] * 382
    assert abs(cosine_similarity(a, b)) < 1e-6


def test_cosine_similarity_opposite():
    """Vectores opuestos tienen similitud -1."""
    a = [1.0] + [0.0] * 383
    b = [-1.0] + [0.0] * 383
    assert abs(cosine_similarity(a, b) + 1.0) < 1e-6


def test_cosine_similarity_empty():
    """Vectores vacíos o longitud distinta devuelven 0."""
    assert cosine_similarity([], []) == 0.0
    assert cosine_similarity([1.0], [1.0, 1.0]) == 0.0


def test_embedding_from_json_none():
    assert embedding_from_json(None) is None
    assert embedding_from_json("") is None


def test_embedding_from_json_invalid():
    assert embedding_from_json("not json") is None
    assert embedding_from_json("[]") is None  # wrong length
    assert embedding_from_json("[1,2,3]") is None  # wrong length


def test_embedding_from_json_valid():
    """JSON con 384 floats se deserializa correctamente."""
    vec = [0.1 * i for i in range(384)]
    import json
    s = json.dumps(vec)
    out = embedding_from_json(s)
    assert out is not None
    assert len(out) == 384
    assert out[0] == 0.0
    assert abs(out[1] - 0.1) < 1e-6


def test_encode_empty_returns_none():
    """Texto vacío o solo espacios devuelve None."""
    assert encode("") is None
    assert encode("   ") is None


def test_encode_returns_384_dims_or_none():
    """encode devuelve None (lib no instalada) o lista de 384 floats."""
    result = encode("hello world")
    if result is None:
        return  # OK: dependencia opcional
    assert isinstance(result, list)
    assert len(result) == 384
    assert all(isinstance(x, (int, float)) for x in result)


def test_encode_returns_none_on_exception():
    """Si model.encode lanza, encode devuelve None y no propaga la excepcion."""
    def raise_runtime(*args, **kwargs):
        raise RuntimeError("OOM")
    with patch("wizard404_core.embeddings._get_model") as mock_get:
        mock_model = type("M", (), {"encode": raise_runtime})()
        mock_get.return_value = mock_model
        out = encode("hello")
    assert out is None


def test_search_by_embeddings_empty_query():
    """Sin query, ordena por order_by y aplica limit/offset."""
    docs = [
        (
            DocumentMetadata(path="/a.txt", name="a.txt", mime_type="text/plain", size_bytes=10, content_preview="A"),
            [0.1] * 384,
        ),
        (
            DocumentMetadata(path="/b.txt", name="b.txt", mime_type="text/plain", size_bytes=20, content_preview="B"),
            [0.2] * 384,
        ),
    ]
    filters = SearchFilters(query="", limit=1, offset=0, order_by="size", order_desc=False)
    results, used = search_by_embeddings(docs, "", filters)
    assert used is False
    assert len(results) == 1
    assert results[0].metadata and results[0].metadata.name == "a.txt"  # menor size primero


def test_search_by_embeddings_with_query_orders_by_similarity():
    """Con query, los resultados se ordenan por similitud (mock: mismo vector = mismo score)."""
    # Dos docs: uno con vector idéntico al que generará "test" (no podemos predecir), usamos dos vectores distintos
    # y comprobamos que search_by_embeddings no falla y devuelve resultados ordenados por score
    v1 = [1.0] + [0.0] * 383
    v2 = [0.9] + [0.0] * 383
    docs = [
        (DocumentMetadata(path="/x.txt", name="x.txt", mime_type="text/plain", size_bytes=1, content_preview="X"), v1),
        (DocumentMetadata(path="/y.txt", name="y.txt", mime_type="text/plain", size_bytes=1, content_preview="Y"), v2),
    ]
    # Query se codificará; si encode devuelve None, search_by_embeddings hace fallback y orden por order_by
    filters = SearchFilters(query="something", limit=10, offset=0)
    results, used = search_by_embeddings(docs, "something", filters)
    assert len(results) <= 2
    if len(results) == 2 and results[0].score != results[1].score:
        assert results[0].score >= results[1].score


def test_search_by_embeddings_pagination():
    """limit y offset se aplican."""
    docs = [
        (
            DocumentMetadata(path=f"/f{i}.txt", name=f"f{i}.txt", mime_type="text/plain", size_bytes=i, content_preview=""),
            [0.0] * 384,
        )
        for i in range(5)
    ]
    filters = SearchFilters(query="", limit=2, offset=1, order_by="name", order_desc=False)
    results, _ = search_by_embeddings(docs, "", filters)
    assert len(results) == 2


def test_search_by_embeddings_order_follows_similarity_when_encode_mocked():
    """
    Con encode mockeado, el primer resultado es el doc cuyo embedding tiene mayor similitud con la query.
    Verifica que el orden depende del score de similitud.
    """
    # Query "mock" = vector [1,0,0,...]; doc A tiene ese mismo vector (sim 1.0), doc B tiene [0,1,0,...] (sim 0)
    query_vec = [1.0] + [0.0] * 383
    vec_high = [1.0] + [0.0] * 383
    vec_low = [0.0, 1.0] + [0.0] * 382
    docs = [
        (DocumentMetadata(path="/a.txt", name="a.txt", mime_type="text/plain", size_bytes=1, content_preview="contrato"), vec_high),
        (DocumentMetadata(path="/b.txt", name="b.txt", mime_type="text/plain", size_bytes=1, content_preview="informe"), vec_low),
    ]
    filters = SearchFilters(query="contrato", limit=10, offset=0)
    with patch("wizard404_core.embeddings.encode", return_value=query_vec):
        results, used = search_by_embeddings(docs, "contrato", filters)
    assert used is True
    assert len(results) == 2
    assert results[0].score >= results[1].score
    assert results[0].metadata and results[0].metadata.name == "a.txt"
    assert results[0].score > 0.99
    assert abs(results[1].score) < 0.01


def test_search_by_embeddings_fallback_when_encode_returns_none():
    """Cuando encode devuelve None y hay query, se usa fallback (orden por order_by) sin excepcion."""
    docs = [
        (DocumentMetadata(path="/z.txt", name="z.txt", mime_type="text/plain", size_bytes=100, content_preview="Z"), [0.0] * 384),
        (DocumentMetadata(path="/a.txt", name="a.txt", mime_type="text/plain", size_bytes=10, content_preview="A"), [0.0] * 384),
    ]
    filters = SearchFilters(query="algo", limit=10, offset=0, order_by="name", order_desc=False)
    with patch("wizard404_core.embeddings.encode", return_value=None):
        results, used = search_by_embeddings(docs, "algo", filters)
    assert used is False
    assert len(results) == 2
    # Fallback ordena por name asc: a.txt antes que z.txt
    assert results[0].metadata and results[0].metadata.name == "a.txt"
    assert results[1].metadata and results[1].metadata.name == "z.txt"
    assert results[0].score == 0.0
    assert results[1].score == 0.0
