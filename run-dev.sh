#!/usr/bin/env bash
# Levanta backend (FastAPI) y frontend (Vite) para probar la aplicacion web.
# Uso: desde la raiz del repo ejecutar ./run-dev.sh
# Ctrl+C detiene el frontend y el backend.
#
# URLs: backend http://localhost:8000 | frontend http://localhost:5173
# El frontend usa la API en localhost:8000 por defecto (VITE_API_URL).
# Para ver los mismos documentos que el CLI, inicia sesion en la web como w404 / w404.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

BACKEND_PID=""
cleanup() {
  if [ -n "$BACKEND_PID" ]; then
    kill "$BACKEND_PID" 2>/dev/null || true
    echo "Backend stopped (PID $BACKEND_PID)."
  fi
  exit 0
}
trap cleanup SIGINT SIGTERM

# Backend: venv debe existir en backend/
if [ ! -d "backend/venv" ]; then
  echo "Crea primero el venv: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# Liberar puerto 8000 si esta en uso (evita "Address already in use")
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti :8000 2>/dev/null || true)
  if [ -n "$PIDS" ]; then
    echo "Port 8000 in use (PIDs: $PIDS). Freeing it..."
    echo "$PIDS" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
fi

echo "Starting backend on http://localhost:8000 ..."
(
  cd backend
  source venv/bin/activate
  exec uvicorn app.main:app --reload
) &
BACKEND_PID=$!

# Dar tiempo al backend a arrancar
sleep 2

# Frontend (usa API en http://localhost:8000 por defecto; mismo usuario que CLI: w404 / w404)
echo "Starting frontend (Vite) on http://localhost:5173 ..."
cd frontend
npm run dev
