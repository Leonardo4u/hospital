"""Pydantic schemas for professionals and auth."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.models.profissional import CargoProfissional


class ProfissionalCreate(BaseModel):
    """Input schema for professional creation."""

    email: str
    nome: str = Field(min_length=1)
    senha: str = Field(min_length=8)
    crm: str | None = None
    cargo: CargoProfissional

    @field_validator("email")
    @classmethod
    def validar_email(cls, value: str) -> str:
        """Validate email format while allowing internal domains like .local."""
        email = value.strip()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Email invalido.")
        return email


class ProfissionalOut(BaseModel):
    """Output schema for professionals."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: str
    cargo: CargoProfissional
    ativo: bool


class TokenOut(BaseModel):
    """Output schema for auth tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    """Input schema for authentication."""

    email: str
    senha: str

    @field_validator("email")
    @classmethod
    def validar_email(cls, value: str) -> str:
        """Validate email format while allowing internal domains like .local."""
        email = value.strip()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Email invalido.")
        return email
