<div align="center">

<img src="../imgs/w404_banner.png" alt="Wizard404" width="720"/>

# Wizard404

### Dokumentensuche & -verwaltung — CLI + Web

**Scannen · Importieren · Suchen · Durchsuchen · Organisieren · Aufräumen.**  
Eine Codebasis. Dieselbe API. Terminal und Browser. Dokumente unter Kontrolle.

[Dokumentation](../) · [Schnellstart](#schnellstart) · [Mitwirken](../../CONTRIBUTING.md)

**Lesen in:** [English](../../README.md) · [Español](README.es.md) · [Polski](README.pl.md) · [中文](README.zh.md) · [Русский](README.ru.md) · [Deutsch](README.de.md)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

**MIT** · Python · FastAPI · React · CLI + Web

</div>

---

> **Wizard404** bündelt Dokumentensuche und -verwaltung (PDF, Text, Office, Bilder, Audio, Video): Verzeichnisse scannen, in den Index importieren, nach Inhalt suchen und von CLI oder Web aus durchsuchen. Für kleine Teams, Unternehmen mit verstreuten Dokumenten und Entwickler, die den Kern (`wizard404_core`) als Bibliothek nutzen.

---

## Was ist Wizard404?

Wizard404 ist eine **Open-Source-Plattform für Dokumentensuche und -verwaltung** — nicht nur ein Dateibrowser. Vollständiger Stack: wiederverwendbarer **Kern** in Python, **REST-API** (FastAPI), interaktive **CLI** (w404) und **Web-App** (React) mit denselben Funktionen.

Klassische Tools zwingen dich, jede Datei zu öffnen. Wizard404 **indiziert Inhalte**, sodass du nach Stichwörtern suchst, nach Typ oder Größe filterst und zum richtigen Dokument springst. Du kannst Ordner scannen, Statistiken nach Erweiterung und Entropie sehen, Dateien nach Typ/Datum/Größe organisieren und Cache sowie Logs aufräumen — im Terminal oder im Browser.

Das System läuft standardmäßig mit **SQLite**. Ein Backend, ein Befehl zum Start.

```bash
# CLI — Menü in 2 Befehlen
./w404

# Web — Backend + Frontend
./run-dev.sh
# API: http://localhost:8000 · App: http://localhost:5173
```

---

## Vorschau

| CLI — Hauptmenü | Scan-Ergebnisse — Entropie & nach Erweiterung |
|----------------|-----------------------------------------------|
| <img src="../imgs/scp-1.png" alt="CLI-Menü" width="400"/> | <img src="../imgs/scp-2.png" alt="Scan-Ergebnisse" width="400"/> |

*Links: Hauptmenü (Scan, Import, Search, Explore, Organize, Cleanup). Rechts: Scan-Ergebnisse mit Zusammenfassung nach Erweiterung und Entropie.*

---

## Was du tun kannst

| Funktion | CLI | Web | Beschreibung |
|----------|-----|-----|--------------|
| **Verzeichnis scannen** | JA | JA | Typen, Größen, Erweiterungen analysieren; Entropie-Zusammenfassung; Drill-down nach Erweiterung. |
| **Dokumente importieren** | JA | JA | Dateien in den Index aufnehmen (Pfad oder „Ordner wählen“ in Chrome/Edge). |
| **Suchen** | JA | JA | Stichwörter im Verzeichnis oder im Index; Filter und semantische Option. |
| **Durchsuchen / Index** | JA | JA | Indizierte Dokumente auflisten; Detail und Zusammenfassung anzeigen. |
| **Organisieren** | JA | NEIN | Dateien nach Typ, Datum oder Größe in Ordner verschieben. |
| **Aufräumen** | JA | NEIN | Cache, Logs, kleine Dateien finden; sicheres Löschen. |

---

## Gelöste Probleme

- **Dokumente nach Inhalt finden** — Verträge, Berichte oder Angebote per Stichwort suchen, ohne jede PDF- oder Office-Datei zu öffnen.
- **Downloads und Ordner organisieren** — Nach Typ, Datum oder Größe sortieren (Organize); Cache und temporäre Dateien erkennen (Cleanup).
- **Ein Ort zum Suchen** — Verzeichnisse scannen, in den Index importieren und auf der Festplatte oder im Index von CLI oder Web aus suchen.

---

## Architektur

Monorepo nach Schichten: Kern, API, CLI, Frontend.

```
backend/          FastAPI-App, Auth, Health, Config
  app/            Routen (auth, documents, scan), Dienste, DB
  wizard404_core  Discovery, Extraktoren (PDF, Office, Text, Bild, Medien), Suche, Semantik, Zusammenfassung
cli/              w404 — TUI-Menüs und direkte Befehle (scan, import, search, organize, cleanup)
frontend/         React + Vite + Tailwind — 16-Bit-UI
docs/             Architektur, Mitwirken, Web-Verzeichniszugriff
```

---

## Schnellstart

### 1. Klonen und Anforderungen

- **Python 3.10+**
- **Node 18+** (optional, für Frontend)
- **SQLite** (Standard; optional PostgreSQL)

```bash
git clone <Repo-URL>
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

### 3. CLI (w404)

Aus dem Repo-Stammverzeichnis:

```bash
./w404
```

### 4. Web

```bash
./run-dev.sh
```

App unter **http://localhost:5173**.

---

## Lizenz

MIT. Siehe [LICENSE](../../LICENSE).

---

## Mitwirken

Siehe [CONTRIBUTING.md](../../CONTRIBUTING.md) und [CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md).

---

<div align="center">

**Wizard404** — Python · FastAPI · React · Vite · Tailwind · CLI + Web

</div>
