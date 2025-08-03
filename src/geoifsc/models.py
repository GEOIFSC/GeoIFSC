"""Data models for user management."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Representa um usuário do PostgreSQL."""

    username: str
    valid_until: Optional[str] = None
    can_login: bool = True


@dataclass
class Group:
    """Representa um grupo do PostgreSQL."""

    name: str
