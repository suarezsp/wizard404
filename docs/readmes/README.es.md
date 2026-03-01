<div align="center">

<img src="../imgs/w404_banner.png" alt="Wizard404" width="720"/>

# Wizard404

### Busqueda y gestion de documentos — CLI + Web

**Escanear · Importar · Buscar · Explorar · Organizar · Limpiar.**  
Un codigo. Misma API. Terminal y navegador. Documentos bajo control.

[Documentacion](../) · [Inicio rapido](#inicio-rapido) · [Contribuir](../../CONTRIBUTING.md)

**Leer en:** [English](../../README.md) · [Espanol](README.es.md) · [Polski](README.pl.md) · [中文](README.zh.md) · [Русский](README.ru.md) · [Deutsch](README.de.md)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

**MIT** · Python · FastAPI · React · CLI + Web

</div>

---

> **Wizard404** centraliza la busqueda y gestion de documentos (PDF, texto, Office, imagenes, audio, video): escanear directorios, importar al indice, buscar por contenido y explorar desde CLI o web. Pensado para equipos pequenos, empresas con documentos dispersos y desarrolladores que reutilizan el nucleo (`wizard404_core`) como libreria.

---

## Que es Wizard404?

Wizard404 es una **plataforma open source de busqueda y gestion de documentos** — no solo un explorador de archivos. Es un stack completo: un **nucleo** reutilizable en Python, una **API REST** (FastAPI), un **CLI** interactivo (w404) y una **app web** (React) con las mismas capacidades.

Las herramientas clasicas obligan a abrir cada archivo. Wizard404 **indiza el contenido**, asi que buscas por palabras clave, filtras por tipo o tamano y saltas al documento correcto. Puedes escanear una carpeta, ver estadisticas por extension y entropia, organizar archivos por tipo/fecha/tamano y limpiar caches y logs — desde la terminal o desde el navegador.

El sistema funciona por defecto con **SQLite**. Un backend, un comando para arrancar.

```bash
# CLI — menu en 2 comandos
./w404

# Web — backend + frontend
./run-dev.sh
# API en http://localhost:8000 · App en http://localhost:5173
```

---

## Vista previa

| CLI — Menu principal | Resultados de scan — Entropia y por extension |
|----------------------|-----------------------------------------------|
| <img src="../imgs/scp-1.png" alt="Menu CLI" width="400"/> | <img src="../imgs/scp-2.png" alt="Resultados scan" width="400"/> |

*Izquierda: Menu principal. Derecha: Resultados del scan con resumen por extension y entropia.*

---

## Que puedes hacer

| Funcion | CLI | Web | Descripcion |
|--------|-----|-----|-------------|
| **Escanear directorio** | Si | Si | Analizar tipos, tamano, extensiones; resumen de entropia; drill-down por extension. |
| **Importar documentos** | Si | Si | Anadir archivos al indice (ruta o Elegir carpeta en Chrome/Edge). |
| **Buscar** | Si | Si | Palabras clave en directorio o en documentos indexados; filtros y opcion semantica. |
| **Explorar / Indice** | Si | Si | Listar documentos indexados; ver detalle y resumen. |
| **Organizar** | Si | — | Mover archivos a carpetas por tipo, fecha o tamano. |
| **Limpiar** | Si | — | Encontrar cache, logs, archivos pequenos; borrado seguro. |

---

## Problema que resuelve

- **Encontrar documentos por contenido** — Buscar contratos, informes u ofertas por palabra clave sin abrir cada PDF u Office.
- **Organizar descargas y carpetas** — Ordenar por tipo, fecha o tamano (Organize); detectar caches y temporales (Cleanup).
- **Un solo lugar para buscar** — Escanear directorios, importar al indice y buscar en disco o en el indice desde CLI o web.

---

## Arquitectura

Monorepo por capas: nucleo, API, CLI, frontend.

```
backend/          App FastAPI, auth, health, config
  app/            Rutas (auth, documents, scan), servicios, db
  wizard404_core  Discovery, extractores (PDF, Office, texto, imagen, media), busqueda, semantica, resumen
cli/              w404 — Menus TUI y comandos directos
frontend/         React + Vite + Tailwind — UI estilo 16-bit
docs/             Arquitectura, contribucion, core como libreria
```

---

## Inicio rapido

### 1. Clonar y requisitos

- **Python 3.10+**
- **Node 18+** (opcional, para frontend)
- **SQLite** (por defecto; opcional PostgreSQL)

```bash
git clone <url-repo>
cd wizard404
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. CLI (w404)

Desde la raiz del repo: `./w404`

### 4. Web

Desde la raiz: `./run-dev.sh` — App en http://localhost:5173

---

## Licencia

MIT. Ver [LICENSE](../../LICENSE). Contribuir: [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

<div align="center">**Wizard404** — Python · FastAPI · React · Vite · Tailwind · CLI + Web</div>
