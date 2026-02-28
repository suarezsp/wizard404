"""
Tests de endpoints de documentos.
"""

import tempfile
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


def test_login(client):
    r = client.post("/auth/login", json={"name": "admin", "password": "admin"})
    if r.status_code != 200:
        r = client.post("/auth/register", json={"name": "admin", "password": "admin"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_search_requires_auth(client):
    r = client.get("/documents/search?q=test")
    assert r.status_code == 401  # no tiene token


def test_search_with_token(client, admin_token):
    r = client.get(
        "/documents/search?q=test",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)
