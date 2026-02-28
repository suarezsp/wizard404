# Arquitectura de Wizard404

Este documento describe la arquitectura del proyecto Wizard404: capas, flujo de datos y responsabilidades de cada componente.

## Visión general

Wizard404 es un monorepo organizado por capas funcionales:

```
┌─────────────────────────────────────────────────────────────────┐
│  Clientes                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ CLI (w404)   │  │ Frontend Web │  │ Otros (API HTTP)      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬─────────────┘  │
└─────────┼─────────────────┼─────────────────────┼────────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend (Python)                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ API FastAPI (auth, documents)                               ││
│  └─────────────────────────────┬───────────────────────────────┘│
│  ┌─────────────────────────────▼───────────────────────────────┐│
│  │ Servicios (app/services): orquestación, lógica de negocio   ││
│  └─────────────────────────────┬───────────────────────────────┘│
│  ┌─────────────────────────────▼───────────────────────────────┐│
│  │ wizard404_core: descubrimiento, extracción, búsqueda, I/O   ││
│  └─────────────────────────────┬───────────────────────────────┘│
│  ┌─────────────────────────────▼───────────────────────────────┐│
│  │ Persistencia: DB (SQLAlchemy), sistema de ficheros          ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Capas del backend

### 1. Núcleo (`wizard404_core`)

- **Ubicación**: `backend/wizard404_core/`
- **Responsabilidad**: Lógica de dominio reutilizable, independiente del transporte (CLI o API).
- **Módulos principales**:
  - **discovery**: Recorre directorios, obtiene metadatos (tipo, tamaño, fecha).
  - **extractors**: Extracción de texto/metadatos por tipo de archivo (PDF, Office, texto, imagen, etc.). Cada extractor se registra en `base.py`; se toleran fallos por archivo (un fallo no detiene el scan).
  - **models**: Modelos de datos (Document, DirectoryStats, SearchFilters, etc.).
  - **search**: Filtrado y búsqueda por keywords/contenido sobre listas de documentos.
- **Dependencias**: Solo estándar de Python y librerías de extracción (PyPDF2, python-docx, etc.). No depende de FastAPI ni de la base de datos de la API.

### 2. API (FastAPI)

- **Ubicación**: `backend/app/`
- **Responsabilidad**: Exponer la funcionalidad vía HTTP (autenticación, documentos, búsqueda).
- **Estructura**:
  - **app/main.py**: Punto de entrada, CORS, lifespan (init DB).
  - **app/api/routes**: `auth` (login, registro) y `documents` (scan, import, search, index, metadatos).
  - **app/api/deps.py**: Dependencias (get_db, get_current_user).
  - **app/services**: Orquestan llamadas a `wizard404_core` y a la base de datos (usuarios, documentos indexados).
  - **app/db**: Modelos SQLAlchemy (User, Document), sesión y configuración.
  - **app/core**: Configuración, seguridad (JWT, hash de contraseñas).

### 3. Flujo de datos típicos

- **Scan de directorio**: Cliente → API `POST /documents/scan` → servicio → `wizard404_core.discover_and_extract()` → respuesta con lista de documentos/metadatos.
- **Importar**: Cliente → `POST /documents/import` con ruta → servicio persiste en DB y opcionalmente en disco.
- **Búsqueda**: Cliente → `GET /documents/search?q=...` (con token) → servicio → `wizard404_core` (list_documents + filtros/búsqueda) o búsqueda sobre documentos indexados en DB.
- **CLI sin API**: La CLI puede usar solo `wizard404_core` (por ejemplo `w404 scan .`) sin necesidad de que la API esté levantada; para Import/Search indexado usa la API si está configurada.

## CLI

- **Ubicación**: `cli/wizard404_cli/`
- **Responsabilidad**: Interfaz de línea de comandos y menú TUI (nativo en terminal).
- **Componentes**:
  - **main**: Punto de entrada; subcomandos (start, scan, import, search, browse, organize, cleanup).
  - **commands**: Implementación de cada comando (scan, import, search, organize, cleanup) usando `wizard404_core` y/o API.
  - **tui/native_menu.py**: Menú interactivo (Simple Term Menu + Rich); orquesta pantallas (scan, import, search, explore, organize, cleanup, index).
  - **tui/loading**: Indicadores de carga para operaciones largas.
  - **api_client**: Cliente HTTP para la API (configuración, list_indexed, search_indexed).
- La CLI añade al `PYTHONPATH` la ruta a `backend` para poder importar `wizard404_core` cuando se ejecuta desde el repo sin instalar.

## Frontend

- **Ubicación**: `frontend/`
- **Stack**: React, Vite, TailwindCSS.
- **Responsabilidad**: Interfaz web para búsqueda y exploración de documentos; consume la API del backend.

## Decisiones técnicas (resumen)

- **Núcleo desacoplado**: Toda la lógica de documentos vive en `wizard404_core` para poder ser usada por CLI y API sin duplicar código.
- **API stateless**: Autenticación JWT; la sesión no se guarda en servidor.
- **Base de datos**: Por defecto SQLite para desarrollo; PostgreSQL recomendado para producción (configurable con `DATABASE_URL`).
- **Extractores tolerantes a fallos**: Si un archivo no puede extraerse (por ejemplo PDF corrupto), se registra el error pero se continúa con el resto.

Para decisiones más detalladas o históricas, se pueden añadir ADRs en `docs/adr/`. Ejemplo: [001-core-desacoplado.md](adr/001-core-desacoplado.md).
