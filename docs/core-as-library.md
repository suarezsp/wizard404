# Usar wizard404_core como librería

El núcleo de Wizard404 (`wizard404_core`) es una librería reutilizable: no depende de FastAPI ni de la base de datos. Puedes usarlo en tus propios scripts o herramientas para escanear directorios, extraer texto y buscar en documentos.

## Instalación

Desde la raíz del repositorio, con el backend como dependencia:

```bash
pip install -e ./backend
```

O clona el repo y añade `backend` al `PYTHONPATH`:

```bash
cd /ruta/a/hack-athon
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

## Ejemplo mínimo

Escaneo de un directorio, extracción de metadatos y búsqueda por palabras clave:

```python
from pathlib import Path
from wizard404_core import discover_and_extract, search_documents
from wizard404_core.models import SearchFilters

# Escanear y extraer documentos de una carpeta
ruta = Path("/ruta/a/mis/documentos")
documentos = list(discover_and_extract(ruta, recursive=True))

# Buscar por contenido (nombre y texto extraído)
filtros = SearchFilters(query="contrato", limit=10)
resultados = search_documents(documentos, filtros)

for r in resultados:
    print(r.metadata.name, "-", r.snippet[:80])
```

Para listar sin búsqueda por texto (solo filtros por tipo o fecha), usa `list_documents(documentos, filtros)`. La API completa está en `backend/wizard404_core/__init__.py` (`__all__`).
