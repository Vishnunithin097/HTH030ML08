from app.api.recommendations import router as recommendations_router
from app.api.users import router as users_router
from app.api.items import router as items_router
from app.api.config import router as config_router
from app.api.metrics import router as metrics_router

__all__ = [
    "recommendations_router",
    "users_router",
    "items_router",
    "config_router",
    "metrics_router",
]
