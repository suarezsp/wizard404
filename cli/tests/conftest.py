"""
Fixtures para tests de la CLI.

Añade el backend al path para que wizard404_core este disponible cuando
se ejecutan los tests desde la raiz del repo (pytest con PYTHONPATH=backend:cli).
"""

import sys
from pathlib import Path

# Asegurar que el backend este en el path (para wizard404_core)
_repo_root = Path(__file__).resolve().parent.parent.parent
_backend = _repo_root / "backend"
if _backend.exists() and str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))
