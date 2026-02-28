# Wizard404

Wizard404 es una plataforma open source para **importar, indexar, buscar y explorar documentos corporativos** (PDF, texto plano y formatos Office básicos) pensada para ser fácil de usar, fácil de extender y fácil de contribuir.

## Problema que resuelve

- **Encontrar documentos por contenido**: buscar contratos, ofertas o informes por palabras clave dentro del texto sin abrir cada PDF o Office.
- **Organizar descargas y carpetas**: ordenar archivos por tipo, fecha o tamaño (Organize) y detectar cachés o archivos temporales para limpiar (Cleanup).
- **Un solo lugar para buscar**: escanear directorios, importar al índice y buscar tanto en disco como en el índice desde CLI o web.

## Impacto

Wizard404 está pensado para **equipos pequeños** y **empresas** con documentos dispersos en carpetas y correo; para **desarrolladores** que quieran reutilizar el núcleo (`wizard404_core`) como librería en sus propias herramientas. Ver [Usar el núcleo como librería](docs/core-as-library.md) para un ejemplo mínimo de uso en código.

## Quick Start (2 minutos)

1. **Clonar y requisitos**: Python 3.10+, Node 18+ (opcional para frontend). Por defecto usa SQLite (no hace falta PostgreSQL).
2. **Backend**: `cd backend && python -m venv venv && source venv/bin/activate` (en Windows: `venv\Scripts\activate`) y `pip install -r requirements.txt`.
3. **CLI**: Desde la raíz del repo ejecuta `./w404` (macOS/Linux) o `w404.bat` (Windows). También: `py -m wizard404_cli.main` con `PYTHONPATH=backend;cli` (Windows: `set PYTHONPATH=backend;cli`). El menú se abre; si el backend no está corriendo, se inicia solo y se configura el token por defecto (usuario `w404`/`w404`).
4. **Listo**: Usa "Scan directory", "Import documents", "Search" o "Explore documents" desde el menú. La API interactiva está en **http://localhost:8000/docs** cuando el backend está activo. El endpoint **GET /health** comprueba estado del servicio y de la base de datos.

## Estructura del repositorio

Este monorepo se organiza por capas funcionales, separando claramente núcleo, interfaz de línea de comandos, API y frontend web:

- **`backend/`**: servicios y lógica de servidor en Python.
  - Dominio: núcleo reutilizable `wizard404_core` (ingesta, análisis, indexado y búsqueda de documentos).
  - Capa de Presentación: API HTTP basada en FastAPI para exponer la funcionalidad a clientes externos (web, integraciones, etc.).
  - Capa de acceso a datos (PostgreSQL + sistema de ficheros).
- **`cli/`**: cliente de línea de comandos **w404** (Wizard404) construido sobre `wizard404_core`.
  - Menú interactivo: `w404` o `w404 start` / `w404 init` (navegación con flechas, Q salir).
  - Comandos directos: import, scan, index, search, browse, **organize**, **cleanup**.
  - **Organize**: mueve archivos a carpetas por tipo, fecha o tamaño (destino por defecto `~/Desktop/Organized`).
  - **Cleanup**: detecta archivos pequeños, cache y logs; muestra resumen y opción de borrado seguro.
- **`frontend/`**: aplicación web creada con React + Vite + TailwindCSS.
  - Interfaz gráfica para búsqueda y exploración de documentos.
  - Estética inspirada en interfaces **16-bit**, con componentes reutilizables (botones, tablas, tarjetas).
  - **Acceso a carpetas locales**: en Chrome/Edge puedes usar "Elegir carpeta" para Scan e Import; en el resto de navegadores se usa "Ruta en el servidor". Ver [docs/web-directorio-local.md](docs/web-directorio-local.md).
- **`docs/`**: documentación extendida del proyecto.
  - Guías de arquitectura, contribución y decisiones técnicas.
  - Material adicional para colaboradores y para explicar el diseño del sistema.

## Visión general

Wizard404 se diseña con estos principios:

- **Open source de verdad**: documentación clara, estructura estándar, licencia abierta y guía de contribución.
- **Calidad sobre complejidad**: se prioriza una arquitectura limpia y mantenible, evitando el over-engineering.
- **CLI primero, web después**: la versión CLI es la base funcional; el frontend web se apoya en la misma API y núcleo.
- **Escalable pero realista**: pensado para funcionar bien en local (demo en portátil) y poder crecer a despliegues en la nube.

La documentación detallada de cada capa (backend, core, CLI, frontend) se irá ampliando en `docs/` y en los READMEs específicos de cada carpeta.

## Instalación rápida (macOS)

### Requisitos

- Python 3.10+
- Node.js 18+
- PostgreSQL

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
python -m scripts.seed_admin  # Usuario admin/admin
```

Por defecto usa **SQLite** (no requiere PostgreSQL). Para usar Postgres:
`export DATABASE_URL=postgresql://user:pass@localhost:5432/wizard404`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Montar todo (backend + frontend) para probar la web

**Opción 1 — Dos terminales (recomendado para desarrollo)**

1. **Terminal 1 — Backend**
   ```bash
   cd backend
   source venv/bin/activate   # Windows: venv\Scripts\activate
   uvicorn app.main:app --reload
   ```
   El API queda en **http://localhost:8000** y la documentación en http://localhost:8000/docs.

2. **Terminal 2 — Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   La app web queda en **http://localhost:5173** (o el puerto que indique Vite). El frontend llama al backend por defecto en `http://localhost:8000` (configurable con `VITE_API_URL`).

**Opción 2 — Un solo comando (macOS/Linux)**

Desde la raíz del repo:

```bash
./run-dev.sh
```

El script levanta el backend en segundo plano y el frontend en primer plano. Al pulsar Ctrl+C se detiene el frontend y el backend. La primera vez asegúrate de tener el venv del backend y las dependencias del frontend instaladas (ver pasos anteriores).

### CLI (comando principal: w404)

```bash
# Opcion 1: scripts en la raiz (usar w404 o wizard404)
./w404                   # Abre el menu interactivo; si el backend no esta corriendo, lo inicia
                         # y configura token por defecto (usuario w404/w404) para Index y busqueda en indice
./w404 start             # Menu interactivo
./w404 init              # Alias de start
./w404 scan .            # Comandos directos
./w404 import docs/
./w404 search contrato --path docs/
./w404 browse docs/
./w404 organize /ruta/origen -d ~/Desktop/Organized --by type
./w404 cleanup /ruta --dry-run

# Tambien: ./wizard404  y  ./wizard404 start  (mismo comportamiento)

# Opcion 2: tener w404 en el PATH (desde la raiz del repo)
pip install -e ./cli
w404 start
w404 scan .

# Opcion 3: manual sin instalar
cd backend && source venv/bin/activate
cd .. && PYTHONPATH=backend:cli python -m wizard404_cli.main start
```

## Licencia

MIT. Ver [LICENSE](LICENSE).

## Contribuir

Queremos que sea fácil contribuir. Consulta la [guía de contribución (CONTRIBUTING.md)](CONTRIBUTING.md) para entorno, estándares de código y proceso. Si tienes ideas de mejora, abre un issue o revisa la sección "Good First Issues" en CONTRIBUTING. Código de conducta: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).