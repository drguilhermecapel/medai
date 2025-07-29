"""API v1 module"""

from .endpoints.auth import router as auth_router
from .endpoints.users import router as users_router
from .endpoints.patients import router as patients_router
from .endpoints.validations import router as validations_router
from .endpoints.notifications import router as notifications_router

__all__ = [
    "auth_router",
    "users_router", 
    "patients_router",
    "validations_router",
    "notifications_router"
]