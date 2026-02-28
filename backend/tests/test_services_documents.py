"""
Tests del servicio de documentos: import_document, import_directory, search, get_document.
"""

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import User
from app.db.session import SessionLocal, init_db
from app.core.security import hash_password
from app.services.documents import (
    import_document,
    import_directory,
    search,
    get_document,
)
from wizard404_core.models import SearchFilters

init_db()


@pytest.fixture
def db() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_user(db: Session) -> User:
    user = db.query(User).filter(User.name == "admin").first()
    if not user:
        user = User(name="admin", password_hash=hash_password("admin"))
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def test_import_document_valid_file(db: Session, admin_user: User, sample_txt_file: Path, tmp_path: Path):
    """Importar archivo válido crea documento en DB con path, nombre, mime, size."""
    original_storage = settings.documents_storage_path
    try:
        settings.documents_storage_path = tmp_path / "storage"
        doc = import_document(sample_txt_file, admin_user.id, db)
        assert doc.id is not None
        assert doc.name == "sample.txt"
        assert doc.mime_type == "text/plain"
        assert doc.size_bytes > 0
        assert doc.owner_id == admin_user.id
        assert doc.content_preview
    finally:
        settings.documents_storage_path = original_storage


def test_import_document_nonexistent_raises(db: Session, admin_user: User):
    with pytest.raises(FileNotFoundError):
        import_document("/nonexistent/path/file.txt", admin_user.id, db)


def test_import_document_unsupported_format_raises(db: Session, admin_user: User, tmp_path: Path):
    f = tmp_path / "file.xyz"
    f.write_text("data")
    with pytest.raises(ValueError):
        import_document(f, admin_user.id, db)


def test_import_directory_multiple_files(
    db: Session, admin_user: User, discovery_tree: Path, tmp_path: Path
):
    """Directorio con varios archivos soportados importa todos."""
    original_storage = settings.documents_storage_path
    try:
        settings.documents_storage_path = tmp_path / "storage"
        docs = import_directory(discovery_tree, admin_user.id, db)
        assert len(docs) >= 2
        names = {d.name for d in docs}
        assert "a.txt" in names or "b.md" in names or "d.txt" in names
    finally:
        settings.documents_storage_path = original_storage


def test_import_directory_with_corrupt_file_imports_rest(
    db: Session, admin_user: User, tmp_path: Path, sample_txt_file: Path, fake_xlsx_file: Path
):
    """Directorio con archivo corrupto (fake .xlsx) importa el resto sin romper."""
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "good.txt").write_text(sample_txt_file.read_text())
    fake_dest = tree / "fake.xlsx"
    fake_dest.write_text("not a zip")
    original_storage = settings.documents_storage_path
    try:
        settings.documents_storage_path = tmp_path / "storage"
        docs = import_directory(tree, admin_user.id, db)
        assert len(docs) >= 1
    finally:
        settings.documents_storage_path = original_storage


def test_search_with_documents(db: Session, admin_user: User, sample_txt_file: Path, tmp_path: Path):
    original_storage = settings.documents_storage_path
    try:
        settings.documents_storage_path = tmp_path / "storage"
        import_document(sample_txt_file, admin_user.id, db)
        results = search(db, admin_user.id, SearchFilters(query="Wizard404", limit=10))
        assert len(results) >= 1
        assert any(r.metadata and "Wizard404" in (r.metadata.content_preview or "") for r in results)
    finally:
        settings.documents_storage_path = original_storage


def test_search_empty_returns_empty_list(db: Session):
    """Usuario sin documentos recibe lista vacía."""
    user = db.query(User).filter(User.name == "emptysearchuser").first()
    if not user:
        user = User(name="emptysearchuser", password_hash=hash_password("x"))
        db.add(user)
        db.commit()
        db.refresh(user)
    results = search(db, user.id, SearchFilters(limit=10))
    assert results == []


def test_get_document_existing(db: Session, admin_user: User, sample_txt_file: Path, tmp_path: Path):
    original_storage = settings.documents_storage_path
    try:
        settings.documents_storage_path = tmp_path / "storage"
        doc = import_document(sample_txt_file, admin_user.id, db)
        found = get_document(db, doc.id, admin_user.id)
        assert found is not None
        assert found.id == doc.id
        assert found.name == doc.name
    finally:
        settings.documents_storage_path = original_storage


def test_get_document_nonexistent(db: Session, admin_user: User):
    assert get_document(db, 99999, admin_user.id) is None
