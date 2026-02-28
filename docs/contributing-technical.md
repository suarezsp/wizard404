# Guía de contribución técnica

Esta guía complementa [CONTRIBUTING.md](../CONTRIBUTING.md) con detalles técnicos para desarrolladores que quieran contribuir código o documentación.

## Entorno de desarrollo

### Backend

- **Python**: 3.10 o superior.
- **Virtualenv**: Se recomienda `python -m venv venv` dentro de `backend/`.
- **Dependencias**: `pip install -r requirements.txt`. Para tests con cobertura: `pip install pytest pytest-cov`.
- **Base de datos**: Por defecto SQLite (fichero en `backend/`). Para PostgreSQL, definir `DATABASE_URL` y crear la base.
- **Arranque**: `uvicorn app.main:app --reload`. Usuario de prueba: `python -m scripts.seed_admin` (admin/admin).

### CLI

- La CLI depende de `wizard404_core`, que vive en `backend/wizard404_core`. Para ejecutar sin instalar:
  - Desde la raíz: `PYTHONPATH=backend:cli python -m wizard404_cli.main start` (o usar los scripts `./w404` que ya configuran el path).
- Instalación editable: `pip install -e ./cli` desde la raíz; entonces el comando `w404` queda en el PATH.

### Frontend

- Node 18+, `npm install` y `npm run dev`. La app espera la API en `http://localhost:8000`.

## Estructura del código

- **Backend**: Ver [architecture.md](architecture.md). Resumen: `app/` (API + servicios + DB), `wizard404_core/` (dominio reutilizable).
- **CLI**: `wizard404_cli/main.py` (entrada y subcomandos), `commands/` (lógica de cada comando), `tui/` (menú interactivo).
- **Tests**: En `backend/tests/`. Nomenclatura `test_*.py`; fixtures en `conftest.py`.

## Tests

- Ejecutar todos los tests del backend: `cd backend && pytest`.
- Con cobertura: `pytest --cov=app --cov=wizard404_core --cov-report=term-missing`. Para fallar si la cobertura está por debajo del 80 %: `pytest --cov=app --cov=wizard404_core --cov-report=term-missing --cov-fail-under=80`.
- Objetivo de cobertura: >80 % en `app` y `wizard404_core` (umbral configurado en `backend/pyproject.toml` en `[tool.coverage.report]`).
- Los tests de API usan `TestClient` de FastAPI; la base de datos es la configurada (habitualmente SQLite en tests). Para aislar el test de registro, se usa un nombre de usuario único (por ejemplo con sufijo aleatorio) para evitar conflictos si el usuario ya existe.

## Estándares de código

- **Python**: PEP 8, type hints en funciones públicas y en parámetros de API.
- **Imports**: Orden estándar (stdlib, terceros, locales). Evitar `*` en imports públicos.
- **Docstrings**: En módulos y en funciones/clases públicas; estilo preferido: descripción en una línea o párrafo corto.
- **Principios**: SOLID, KISS, DRY, YAGNI. Evitar over-engineering.

## Añadir un nuevo extractor

1. Crear un módulo en `backend/wizard404_core/extractors/` que implemente la interfaz `Extractor` (método `extract(path) -> DocumentMetadata | None`).
2. Registrar con `register_extractor(MiExtractor())` en el mismo módulo.
3. Añadir tests en `backend/tests/test_extractors.py` para al menos un archivo de ejemplo del formato.

## Añadir un endpoint en la API

1. Definir la ruta en `app/api/routes/` (auth o documents).
2. Si hay lógica de negocio, ponerla en `app/services/` y llamarla desde el router.
3. Añadir tests en `backend/tests/test_api_documents.py` (o el archivo que corresponda) usando `TestClient` y, si aplica, el fixture `admin_token`.

## Documentación

- Documentación de arquitectura y decisiones: en `docs/`.
- ADRs (Architecture Decision Records): opcional en `docs/adr/` con formato título, contexto, decisión y consecuencias.
- README y CONTRIBUTING: mantener actualizados (incl. comando `w404` e instalación).

## Logs

- Los agentes y scripts que generen logs siguen el formato acordado en `agents/logs/` cuando aplique. En el código, usar el módulo `logging` estándar con niveles adecuados (DEBUG, INFO, WARNING, ERROR).

## Dudas

- Abre un issue en el repositorio o comenta en un PR existente. Para decisiones de diseño que afecten a varias partes, se recomienda describirlas en un issue o en un ADR en `docs/adr/`.
