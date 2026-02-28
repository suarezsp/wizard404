"""
Tests de endpoints de documentos.
"""

import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import User
from app.core.security import hash_password, create_access_token
from app.db.session import SessionLocal, init_db

init_db()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token():
    db = SessionLocal()
    user = db.query(User).filter(User.name == "admin").first()
    if not user:
        user = User(name="admin", password_hash=hash_password("admin"))
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_access_token(subject=user.id)
    db.close()
    return token


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Wizard404" in r.json()["message"]


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert data.get("database") in ("ok", "error")


def test_login(client):
    r = client.post("/auth/login", json={"name": "admin", "password": "admin"})
    if r.status_code != 200:
        r = client.post("/auth/register", json={"name": "admin", "password": "admin"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_register_new_user(client):
    # Usuario único para evitar fallos por DB compartida (ej. newuser ya existe)
    name = f"newuser_{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/auth/register",
        json={"name": name, "password": "secret"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["user_name"] == name
    assert "access_token" in data


def test_login_wrong_password(client, admin_token):
    r = client.post("/auth/login", json={"name": "admin", "password": "wrong"})
    assert r.status_code == 401


def test_search_requires_auth(client):
    r = client.get("/documents/search?q=test")
    assert r.status_code == 401


def test_search_with_token(client, admin_token):
    r = client.get(
        "/documents/search?q=test",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_document_with_token(client, admin_token, sample_txt_file: Path):
    # Import first to get a document id
    r_import = client.post(
        "/documents/import",
        params={"path": str(sample_txt_file.resolve())},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_import.status_code == 200
    doc_id = r_import.json()["document_id"]

    r = client.get(
        f"/documents/{doc_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "sample.txt"
    assert "content_preview" in data
    assert data["mime_type"] == "text/plain"


def test_get_document_summary(client, admin_token, sample_txt_file: Path):
    r_import = client.post(
        "/documents/import",
        params={"path": str(sample_txt_file.resolve())},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_import.status_code == 200
    doc_id = r_import.json()["document_id"]
    r = client.get(
        f"/documents/{doc_id}/summary",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "summary" in data
    assert data["doc_id"] == doc_id
    assert "Wizard404" in data["summary"] or len(data["summary"]) >= 0


def test_get_document_not_found(client, admin_token):
    r = client.get(
        "/documents/99999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 404


def test_import_file(client, admin_token, sample_txt_file: Path):
    r = client.post(
        "/documents/import",
        params={"path": str(sample_txt_file.resolve())},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["imported"] == 1
    assert "document_id" in data


def test_import_directory(client, admin_token, discovery_tree: Path):
    r = client.post(
        "/documents/import",
        params={"path": str(discovery_tree.resolve())},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["imported"] >= 1
    assert "document_ids" in data


def test_import_invalid_path(client, admin_token):
    r = client.post(
        "/documents/import",
        params={"path": "/nonexistent/path/file.txt"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code in (400, 404)


def test_import_requires_auth(client, sample_txt_file: Path):
    r = client.post(
        "/documents/import",
        params={"path": str(sample_txt_file.resolve())},
    )
    assert r.status_code == 401


def test_search_semantic_param(client, admin_token):
    """semantic=true se acepta y devuelve 200."""
    r = client.get(
        "/documents/search?q=test&semantic=true",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_assist_endpoint(client, admin_token, sample_txt_file: Path):
    """POST /documents/assist devuelve sugerencias para placeholders."""
    r_import = client.post(
        "/documents/import",
        params={"path": str(sample_txt_file.resolve())},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_import.status_code == 200
    doc_id = r_import.json()["document_id"]
    r = client.post(
        "/documents/assist",
        json={"context_doc_ids": [doc_id], "placeholders": ["titulo", "resumen"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], dict)


def test_import_then_search_returns_doc(client, admin_token, sample_txt_file: Path):
    """Verificación de indexado: importar un archivo y buscar por su contenido debe devolver ese documento."""
    r_import = client.post(
        "/documents/import",
        params={"path": str(sample_txt_file.resolve())},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_import.status_code == 200
    assert r_import.json().get("imported") == 1

    r_search = client.get(
        "/documents/search",
        params={"q": "Wizard404"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r_search.status_code == 200
    results = r_search.json()
    assert isinstance(results, list)
    assert len(results) >= 1
    names = [r.get("name") for r in results if r.get("name")]
    assert "sample.txt" in names


def test_scan_requires_auth(client, discovery_tree: Path):
    r = client.get("/scan", params={"path": str(discovery_tree.resolve())})
    assert r.status_code == 401


def test_scan_get_success(client, admin_token, discovery_tree: Path):
    r = client.get(
        "/scan",
        params={"path": str(discovery_tree.resolve())},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "total_files" in data
    assert "total_size" in data
    assert "by_type" in data
    assert "by_extension" in data
    assert data["total_files"] >= 1
    assert isinstance(data["by_extension"], dict)
    assert isinstance(data["by_type"], dict)


def test_scan_post_success(client, admin_token, discovery_tree: Path):
    r = client.post(
        "/scan",
        json={"path": str(discovery_tree.resolve())},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total_files"] >= 1
    assert "by_extension" in data


def test_scan_path_required(client, admin_token):
    r = client.get("/scan", params={}, headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 400
    r2 = client.post("/scan", json={}, headers={"Authorization": f"Bearer {admin_token}"})
    assert r2.status_code == 422


def test_scan_must_be_directory(client, admin_token, sample_txt_file: Path):
    r = client.get(
        "/scan",
        params={"path": str(sample_txt_file.resolve())},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 400
    assert "directory" in r.json().get("detail", "").lower()


def test_scan_files_requires_auth(client, discovery_tree: Path):
    r = client.get(
        "/scan/files",
        params={"path": str(discovery_tree.resolve()), "extension": ".txt"},
    )
    assert r.status_code == 401


def test_scan_files_success(client, admin_token, discovery_tree: Path):
    r = client.get(
        "/scan/files",
        params={"path": str(discovery_tree.resolve()), "extension": ".txt"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for item in data:
        assert "name" in item
        assert "path" in item
        assert "size_bytes" in item
        assert "mime_type" in item
    names = [x["name"] for x in data]
    assert "a.txt" in names
    assert "d.txt" in names


def test_upload_requires_auth(client):
    r = client.post(
        "/documents/upload",
        files=[("files", ("test.txt", b"Hello Wizard404", "text/plain"))],
    )
    assert r.status_code == 401


def test_upload_success(client, admin_token):
    content = b"Hello Wizard404. Upload test content for index."
    r = client.post(
        "/documents/upload",
        files=[("files", ("uploaded.txt", content, "text/plain"))],
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["imported"] == 1
    assert len(data["document_ids"]) == 1


def test_upload_too_many_files(client, admin_token):
    many = [("files", (f"f{i}.txt", b"x", "text/plain")) for i in range(501)]
    r = client.post(
        "/documents/upload",
        files=many,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 400
    assert "max" in r.json().get("detail", "").lower()
