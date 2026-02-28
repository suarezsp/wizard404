# Resumen por apartado — Wizard404

Documento explicativo por componente para demo, revisión y cierre del proyecto según behaviour.

**Impacto**: Wizard404 está pensado para equipos pequeños y empresas con documentos dispersos; para desarrolladores que reutilizan el núcleo (`wizard404_core`) como librería. Ver [docs/core-as-library.md](core-as-library.md).

---

## Backend

- **Qué es**: API REST (FastAPI) y núcleo reutilizable de dominio (`wizard404_core`).
- **Tecnologías**: Python 3.10+, FastAPI, SQLAlchemy, SQLite/PostgreSQL, JWT (auth).
- **Estructura**:
  - `app/`: API (rutas auth y documents), servicios, modelos de DB, configuración y seguridad.
  - `wizard404_core/`: descubrimiento de archivos, extractores (PDF, Office, texto, imagen), modelos de datos, búsqueda y filtrado. Sin dependencias de FastAPI.
- **Puntos de entrada**: `uvicorn app.main:app`; usuario demo con `python -m scripts.seed_admin`.
- **Tests**: `pytest` en `backend/tests/` (API, servicios, core, extractores, organize). Cobertura con `pytest --cov=app --cov=wizard404_core --cov-report=term-missing`; umbral configurado en `pyproject.toml`.

---

## CLI

- **Qué es**: Cliente de línea de comandos **w404** (Wizard404) con menú TUI y comandos directos.
- **Tecnologías**: Python, Typer, Rich, Simple Term Menu. Depende de `wizard404_core` (y opcionalmente de la API para índice).
- **Estructura**:
  - `wizard404_cli/main.py`: entrada y subcomandos (start, scan, import, search, browse, organize, cleanup).
  - `commands/`: lógica de cada comando (scan, import, search, organize, cleanup).
  - `tui/`: menú interactivo; `native_menu.py` orquesta; `menu_scan.py`, `menu_search.py`, `menu_organize.py`, `menu_cleanup.py`, `menu_explore.py`, `menu_import.py` por dominio; `common.py` con utilidades compartidas; `loading.py` para indicadores de carga.
- **Uso**: Desde la raíz, `./w404` o `./w404 start` (menú); `./w404 scan .`, `./w404 organize /ruta --by type`, etc. Con backend en PATH: `pip install -e ./cli` y `w404 start`.

---

## Frontend

- **Qué es**: Aplicación web para búsqueda y exploración de documentos.
- **Tecnologías**: React, Vite, TailwindCSS. Consume la API del backend.
- **Uso**: `npm install` y `npm run dev` en `frontend/`; API en `http://localhost:8000`, frontend en `http://localhost:5173`.

---

## Tests

- **Backend**: ~80 tests en `backend/tests/` (API, auth, documentos, extractores, discovery, search, models, organize, services). Un test de registro usa usuario único para evitar conflictos en DB compartida. Cobertura >80 % en `app` y `wizard404_core` (configuración en `backend/pyproject.toml`). Comando: `cd backend && pytest` (con cobertura: `pytest --cov=app --cov=wizard404_core --cov-report=term-missing`).
- **CLI**: Sin tests E2E automatizados en el plan; la CLI se prueba manualmente (menú y comandos directos).
- **Frontend**: Vitest + React Testing Library en `frontend/`. Tests para: App, Home, Scan, Search, DocumentDetail, Login, Import, MageWizard, ToastList, ProgressBar, RouteTransition, ParticleBackground, Button, contextos (Toast, Mage), hooks (useTypewriter), api/client, data/mageDialogue. Comando: `cd frontend && npm run test` (o `npm run test -- --run` para una sola ejecución).

---

## Demo y cierre

- **Reproducir la demo**: (1) Arrancar backend: `cd backend && source venv/bin/activate && uvicorn app.main:app`. (2) Opcional — frontend: `cd frontend && npm run dev`. (3) CLI: desde la raíz `./w404` (menú) o `./w404 start`. Mostrar: Scan directory, Import documents, Index/Search (directorio e índice), Explore documents, Organize files, Cleanup. En web: Login, Scan con barra de progreso, Search, detalle de documento con "Volver a resultados".
- **Video de demo**: Grabar un video corto con el flujo anterior y enlazarlo aquí o en el README cuando esté disponible. El proyecto se considera cerrado cuando exista demo en video y confirmación del responsable (según agents/behaviour.txt).
- Este documento y los de `docs/` (arquitectura, contribución técnica, core-as-library) sirven como documento explicativo por apartado para el cierre según behaviour.
