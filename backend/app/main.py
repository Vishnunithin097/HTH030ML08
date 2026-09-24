from contextlib import asynccontextmanager
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.validator import artifact_validator
from app.core.feature_extraction import feature_store
from app.core.catalog import catalog
from app.auth.router import router as auth_router
from app.api.recommendations import router as recommendations_router
from app.api.users import router as users_router
from app.api.items import router as items_router
from app.api.config import router as config_router
from app.api.metrics import router as metrics_router
from app.api.simulation import router as simulation_router
from app.api.images import router as images_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate and load artifacts once at startup
    logger.info("Initializing pre-trained ML models and catalog...")
    val_report = artifact_validator.validate_all()
    catalog.initialize_from_metadata()
    if val_report["status"] != "ready":
        logger.warning(f"Startup Artifact Validation Warnings: {val_report.get('errors')}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Cold-Start-Aware Hybrid Recommendation Engine with Business Guardrails API",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness check confirming server responsiveness."""
    return {"status": "ok"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe validating database and ML model artifact health."""
    val_report = artifact_validator.validate_all()
    return val_report


# Mount product-visuals and product images static files
_REPO_DIR = Path(__file__).resolve().parent.parent.parent
_VISUALS_DIR = _REPO_DIR / "image_dataset" / "product_visuals"
_IMAGES_DIR = _REPO_DIR / "image_dataset" / "images"
_VISUALS_DIR.mkdir(parents=True, exist_ok=True)
_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/product-visuals", StaticFiles(directory=str(_VISUALS_DIR)), name="product_visuals")
app.mount("/images/products", StaticFiles(directory=str(_IMAGES_DIR)), name="product_images")
app.mount("/image_dataset/images", StaticFiles(directory=str(_IMAGES_DIR)), name="image_dataset_images")

# Mount Routers
app.include_router(auth_router)
app.include_router(recommendations_router)
app.include_router(users_router)
app.include_router(items_router)
app.include_router(config_router)
app.include_router(metrics_router)
app.include_router(simulation_router)
app.include_router(images_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
