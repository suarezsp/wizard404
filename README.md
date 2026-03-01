<div align="center">

<img src="docs/imgs/w404_banner.png" alt="Wizard404" width="720"/>

# Wizard404

### Document Search & Management — CLI + Web

**Scan · Import · Search · Explore · Organize · Cleanup.**  
One codebase. Same API. Terminal and browser. Documents under control.

[Documentation](docs/) · [Quick Start](#quick-start) · [Contributing](CONTRIBUTING.md)

**Read in:** [English](README.md) · [Español](docs/readmes/README.es.md) · [Polski](docs/readmes/README.pl.md) · [中文](docs/readmes/README.zh.md) · [Русский](docs/readmes/README.ru.md) · [Deutsch](docs/readmes/README.de.md)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

**MIT** · Python · FastAPI · React · CLI + Web

</div>

---

> **Wizard404** centralizes document search and management (PDF, text, Office, images, audio, video): scan directories, import to the index, search by content, and explore from CLI or web. Built for small teams, companies with scattered documents, and developers who reuse the core (`wizard404_core`) as a library.

---

## What is Wizard404?

Wizard404 is an **open-source document search and management platform** — not only a file browser. It is a full stack: a reusable **core** in Python, a **REST API** (FastAPI), an interactive **CLI** (w404), and a **web app** (React) with the same capabilities.

Traditional tools make you open each file. Wizard404 **indexes content**, so you search by keywords, filter by type or size, and jump to the right document. You can scan a folder, see stats by extension and entropy, organize files by type/date/size, and clean up caches and logs — from the terminal or from the browser.

The entire system runs with **SQLite** by default. One backend, one command to start.

```bash
# CLI — menu in 2 commands
./w404

# Web — backend + frontend
./run-dev.sh
# API at http://localhost:8000 · App at http://localhost:5173
```

---

## Preview

| CLI — Main menu | Scan results — Entropy & by extension |
|-----------------|---------------------------------------|
| <img src="docs/imgs/scp-1.png" alt="CLI menu" width="400"/> | <img src="docs/imgs/scp-2.png" alt="Scan results" width="400"/> |

*Left: Main menu (Scan, Import, Search, Explore, Organize, Cleanup). Right: Scan results with summary by extension and entropy.*

---

## What You Can Do

| Feature | CLI | Web | Description |
|--------|-----|-----|-------------|
| **Scan directory** | YES | YES | Analyze types, sizes, extensions; entropy summary; drill-down by extension. |
| **Import documents** | YES | YES | Add files to the index (path or “Choose folder” in Chrome/Edge). |
| **Search** | YES | YES | Keywords in directory or in indexed documents; filters and semantic option. |
| **Explore / Index** |YES | YES | List indexed documents; view detail and summary. |
| **Organize** | YES | NO | Move files into folders by type, date, or size. |
| **Cleanup** | YES | NO | Find cache, logs, tiny files; safe delete. |

*Import and “view indexed” are best used from the **web** (Explore + Import). CLI redirects to the app for a consistent experience.*

---

## Problem It Solves

- **Find documents by content** — Search contracts, reports, or quotes by keyword without opening every PDF or Office file.
- **Organize downloads and folders** — Sort by type, date, or size (Organize); detect caches and temp files (Cleanup).
- **One place to search** — Scan directories, import to the index, and search on disk or in the index from CLI or web.

---

## Architecture

Monorepo by layer: core, API, CLI, frontend.

```
backend/          FastAPI app, auth, health, config
  app/            Routes (auth, documents, scan), services, db
  wizard404_core  Discovery, extractors (PDF, Office, text, image, media), search, semantic, summary
cli/              w404 — TUI menus and direct commands (scan, import, search, organize, cleanup)
frontend/         React + Vite + Tailwind — 16-bit style UI, Scan, Import, Search, Explore, Document detail
docs/             Architecture, contributing, web directory access, core-as-library
```

---

## Quick Start

### 1. Clone and requirements

- **Python 3.10+**
- **Node 18+** (optional, for frontend)
- **SQLite** (default; optional PostgreSQL)

```bash
git clone <repo-url>
cd wizard404
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Optional: `python -m scripts.seed_admin` for default user. API at **http://localhost:8000**, docs at **http://localhost:8000/docs**.

### 3. CLI (w404)

From repo root:

```bash
./w404
```

Opens the interactive menu. If the backend is not running, the CLI can start it and set the default token (user `w404` / `w404`). Then use **Scan directory**, **Import documents**, **Search**, **Explore**, **Organize**, **Cleanup**.

Direct commands:

```bash
./w404 scan .
./w404 import docs/     # lists documents in path (does not persist to index)
./w404 index docs/      # persists path to backend index (path must exist on server)
./w404 search contrato --path docs/
./w404 organize /path -d ~/Desktop/Organized --by type
./w404 cleanup /path --dry-run
```

**Note:** `import` only lists documents in the given path; `index` sends the path to the backend and persists files to the index (the path must be accessible by the server).

### 4. Web (backend + frontend)

From repo root:

```bash
./run-dev.sh
```

Backend in background, frontend in foreground. App at **http://localhost:5173**. First time: ensure backend venv and `frontend/node_modules` are installed (steps 2 and `cd frontend && npm install`).

---

## Impact & Audience

- **Small teams and companies** with documents scattered across folders and email.
- **Developers** who want to reuse the core as a library — see [Using the core as a library](docs/core-as-library.md).

---

## Development

```bash
# Backend tests
cd backend && source venv/bin/activate && pytest tests -v

# Frontend tests
cd frontend && npm run test

# Lint / format per project (backend: ruff/black; frontend: eslint/prettier)
```

---

## License

MIT. See [LICENSE](LICENSE).

---

## Contributing

We want contributions to be easy. See the [contributing guide (CONTRIBUTING.md)](CONTRIBUTING.md) for setup, code standards, and process. For ideas, open an issue or check “Good First Issues” in CONTRIBUTING. Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

<div align="center">

**Wizard404** — Python · FastAPI · React · Vite · Tailwind · CLI + Web

</div>
