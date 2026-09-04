"""Compatibilidade: novos módulos devem usar `extensions.db` e os modelos SQLAlchemy."""

from extensions import db

__all__ = ["db"]
