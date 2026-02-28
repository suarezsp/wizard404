#!/usr/bin/env python3
"""
Crea usuario admin de demo.

Ejecutar: python -m scripts.seed_admin
Requiere que la DB exista y las tablas esten creadas.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.db.models import User
from app.db.session import SessionLocal, init_db

init_db()
db = SessionLocal()
if db.query(User).filter(User.name == "admin").first():
    print("Admin user already exists.")
else:
    user = User(name="admin", password_hash=hash_password("admin"))
    db.add(user)
    db.commit()
    print("Admin user created (admin/admin).")
db.close()
