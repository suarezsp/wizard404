# Guía de contribución a Wizard404

Gracias por tu interés en contribuir a Wizard404. Este documento explica cómo montar el entorno y contribuir al proyecto.

## Requisitos

- Python 3.10+
- Node.js 18+
- PostgreSQL
- macOS (el proyecto se desarrolla en MacBook Pro)

## Montar el entorno

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Por defecto se usa SQLite (no requiere instalación). Para PostgreSQL:

```sql
CREATE DATABASE wizard404;
```

Y configurar en `.env` o variable de entorno:

```
DATABASE_URL=postgresql://usuario:password@localhost:5432/wizard404
```

Iniciar la API:

```bash
uvicorn app.main:app --reload
```

Crear usuario admin de demo:

```bash
python -m scripts.seed_admin
```

### CLI

```bash
cd cli
pip install -r requirements.txt
# Asegúrate de tener el backend en el path (ejecutar desde la raíz del proyecto)
python -m wizard404_cli.main scan .
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

La API debe estar corriendo en `http://localhost:8000` y el frontend en `http://localhost:5173`.

## Ejecutar tests

Ejecuta backend y CLI por separado (evita conflicto de conftest):

```bash
# Backend (desde repo)
cd backend && ./venv/bin/python -m pytest tests -v

# CLI (desde repo)
PYTHONPATH=backend:cli ./backend/venv/bin/python -m pytest cli/tests -v
```

No ejecutes `pytest backend/tests cli/tests` en una sola invocación desde la raíz.

## Estándares de código

- **Python**: PEP 8, type hints donde sea posible.
- **JavaScript/React**: ESLint, componentes funcionales.
- **Tests**: Cada nueva funcionalidad debe incluir tests. Usamos pytest (backend y CLI); el frontend puede usar Vitest si se añade.

## Buenas prácticas

- SOLID, KISS, DRY, YAGNI.
- Evitar over-engineering.
- Documentar decisiones técnicas en comentarios o en `docs/`.

## Good First Issues

- Mejorar mensajes de error en la CLI.
- Añadir más formatos de documento (ej. ODT).
- Traducción del README al inglés.
- Mejoras de accesibilidad en el frontend.

## Proceso de contribución

1. Abre un issue describiendo el cambio.
2. Crea una rama desde `main`.
3. Implementa los cambios con tests.
4. Abre un Pull Request con descripción clara.
