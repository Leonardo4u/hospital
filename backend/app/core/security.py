"""Security helpers for password hashing and JWT."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt


def hash_senha(senha: str) -> str:
    """Generate a bcrypt hash for a password."""
    senha_bytes = senha.encode("utf-8")
    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, hash_: str) -> bool:
    """Validate a password against a bcrypt hash."""
    return bcrypt.checkpw(senha.encode("utf-8"), hash_.encode("utf-8"))


def criar_access_token(dados: dict) -> str:
    """Create a signed access token."""
    from backend.app.core.config import settings

    expira_em = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _criar_token(dados, expira_em, settings.SECRET_KEY, settings.ALGORITHM)


def criar_refresh_token(dados: dict) -> str:
    """Create a signed refresh token."""
    from backend.app.core.config import settings

    expira_em = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _criar_token(dados, expira_em, settings.SECRET_KEY, settings.ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Decode a token or raise HTTP 401."""
    from backend.app.core.config import settings

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return dict(payload)


def _criar_token(dados: dict, expira_em: datetime, secret_key: str, algorithm: str) -> str:
    payload = dict(dados)
    payload["exp"] = expira_em
    return jwt.encode(payload, secret_key, algorithm=algorithm)
