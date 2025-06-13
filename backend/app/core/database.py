"""
Database module - Compatibility layer for database session management.
Provides get_db function for dependency injection.
"""

from app.db.session import get_db

__all__ = ["get_db"]
