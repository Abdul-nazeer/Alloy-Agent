"""Database module."""

from .schema import get_connection, init_database

__all__ = ["get_connection", "init_database"]
