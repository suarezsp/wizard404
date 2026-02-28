"""
config de la app

Carga desde variables de entorno. Valores por defecto para dev local.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # API
    app_name: str = "Wizard404"
    debug: bool = False

    # DB: por defecto SQLit para DEMO (funciona sin Postgres). Para Postgres: DATABASE_URL=postgresql://...
    database_url: str = "sqlite:///./data/wizard404.db"

    # Auth
    secret_key: str = "wizard404-dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24h

    # Documentos
    documents_storage_path: Path = Path("./data/documents").resolve()
    max_import_file_bytes: int = 50 * 1024 * 1024  # 50 MB por archivo
    max_upload_files_per_request: int = 500  # max archivos en POST /documents/upload

    # API paginación
    max_list_limit: int = 500
    max_search_limit: int = 100


settings = Settings()
