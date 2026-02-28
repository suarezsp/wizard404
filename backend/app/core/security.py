"""
Auth y tokens

Hash de contraseñas con bcrypt y JWT para tokens.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de la contraseña en texto plano (para almacenar en DB)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Comprueba si la contraseña en texto plano coincide con el hash; devuelve True/False."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(subject: str | int) -> str:
    """Genera un JWT con sub=subject y expiración según settings; devuelve el token en string."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> str | None:
    """Decodifica el JWT y devuelve el subject (sub); None si el token es inválido o ha expirado."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload.get("sub")
    except JWTError:
        return None
