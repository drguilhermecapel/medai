"""API v1 endpoints"""

from .auth import router as auth_router
from .users import router as users_router
from .patients import router as patients_router
from .validations import router as validations_router
from .notifications import router as notifications_router

__all__ = [
    "auth_router",
    "users_router", 
    "patients_router",
    "validations_router",
    "notifications_router"
]