"""
Specialty API endpoints package
"""

from .dermatology import router as dermatology_router

__all__ = [
    "dermatology_router",
]