<div align="center">

<img src="../imgs/w404_banner.png" alt="Wizard404" width="720"/>

# Wizard404

### Wyszukiwanie i zarządzanie dokumentami — CLI + Web

**Skanuj · Importuj · Szukaj · Przeglądaj · Organizuj · Czyść.**  
Jedna baza kodu. Ta sama API. Terminal i przeglądarka. Dokumenty pod kontrolą.

[Dokumentacja](../) · [Szybki start](#szybki-start) · [Wkład](../../CONTRIBUTING.md)

**Czytaj w:** [English](../../README.md) · [Español](README.es.md) · [Polski](README.pl.md) · [中文](README.zh.md) · [Русский](README.ru.md) · [Deutsch](README.de.md)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

**MIT** · Python · FastAPI · React · CLI + Web

</div>

---

> **Wizard404** centralizuje wyszukiwanie i zarządzanie dokumentami (PDF, tekst, Office, obrazy, audio, wideo): skanuj katalogi, importuj do indeksu, szukaj po treści i przeglądaj z CLI lub przeglądarki. Dla małych zespołów, firm z rozproszonymi dokumentami i deweloperów korzystających z rdzenia (`wizard404_core`) jako biblioteki.

---

## Czym jest Wizard404?

Wizard404 to **platforma open source do wyszukiwania i zarządzania dokumentami** — nie tylko przeglądarka plików. Pełny stos: **rdzeń** w Pythonie, **REST API** (FastAPI), **CLI** (w404) i **aplikacja webowa** (React) z tymi samymi możliwościami.

Tradycyjne narzędzia każą otwierać każdy plik. Wizard404 **indeksuje treść**, więc szukasz po słowach kluczowych, filtrujesz po typie lub rozmiarze i przechodzisz do właściwego dokumentu. Możesz skanować folder, oglądać statystyki po rozszerzeniu i entropii, organizować pliki po typie/dacie/rozmiarze i czyścić cache oraz logi — z terminala lub przeglądarki.

Domyślnie system działa na **SQLite**. Jeden backend, jedna komenda.

```bash
# CLI — menu w 2 komendach
./w404

# Web — backend + frontend
./run-dev.sh
# API: http://localhost:8000 · Aplikacja: http://localhost:5173
```

---

## Podgląd

| CLI — Menu główne | Wyniki skanowania — Entropia i rozszerzenia |
|-------------------|--------------------------------------------|
| <img src="../imgs/scp-1.png" alt="Menu CLI" width="400"/> | <img src="../imgs/scp-2.png" alt="Wyniki scan" width="400"/> |

*Lewo: Menu główne. Prawo: Wyniki skanowania z podsumowaniem po rozszerzeniu i entropii.*

---

## Co możesz zrobić

| Funkcja | CLI | Web | Opis |
|--------|-----|-----|------|
| **Skanuj katalog** | TAK | TAK | Analiza typów, rozmiarów, rozszerzeń; podsumowanie entropii; drill-down po rozszerzeniu. |
| **Importuj dokumenty** | TAK | TAK | Dodawanie plików do indeksu (ścieżka lub „Wybierz folder” w Chrome/Edge). |
| **Szukaj** | TAK | TAK | Słowa kluczowe w katalogu lub w indeksie; filtry i opcja semantyczna. |
| **Przeglądaj / Indeks** | TAK | TAK | Lista dokumentów w indeksie; szczegóły i podsumowanie. |
| **Organizuj** | TAK | NIE | Przenoszenie plików do folderów po typie, dacie lub rozmiarze. |
| **Czyść** | TAK | NIE | Wyszukiwanie cache, logów, małych plików; bezpieczne usuwanie. |

---

## Rozwiązywany problem

- **Znajdowanie dokumentów po treści** — Szukaj kontraktów, raportów, ofert po słowach kluczowych bez otwierania każdego PDF czy Office.
- **Organizacja pobranych i folderów** — Sortowanie po typie, dacie, rozmiarze (Organize); wykrywanie cache i plików tymczasowych (Cleanup).
- **Jedno miejsce do wyszukiwania** — Skanuj katalogi, importuj do indeksu i szukaj na dysku lub w indeksie z CLI lub przeglądarki.

---

## Architektura

Monorepo warstwami: rdzeń, API, CLI, frontend.

```
backend/          Aplikacja FastAPI, auth, health, config
  app/            Trasy (auth, documents, scan), serwisy, db
  wizard404_core  Discovery, ekstraktory (PDF, Office, tekst, obraz, media), wyszukiwanie, semantyka, podsumowanie
cli/              w404 — menu TUI i komendy (scan, import, search, organize, cleanup)
frontend/         React + Vite + Tailwind — UI w stylu 16-bit
docs/             Architektura, wkład, dostęp do katalogu w przeglądarce
```

---

## Szybki start

### 1. Klonowanie i wymagania

- **Python 3.10+**
- **Node 18+** (opcjonalnie, dla frontendu)
- **SQLite** (domyślnie; opcjonalnie PostgreSQL)

```bash
git clone <url-repo>
cd hack-athon
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

Z katalogu głównego repozytorium:

```bash
./w404
```

### 4. Web

```bash
./run-dev.sh
```

Aplikacja: **http://localhost:5173**.

---

## Licencja

MIT. Zobacz [LICENSE](../../LICENSE).

---

## Wkład

Zobacz [CONTRIBUTING.md](../../CONTRIBUTING.md) i [CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md).

---

<div align="center">

**Wizard404** — Python · FastAPI · React · Vite · Tailwind · CLI + Web

</div>
