from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.auth.router import router as auth_router
from app.api.recommendations import router as recommendations_router
from app.api.users import router as users_router
from app.api.items import router as items_router
from app.api.config import router as config_router
from app.api.metrics import router as metrics_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Cold-Start-Aware Hybrid Recommendation Engine with Business Guardrails API",
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
    """Health check endpoint confirming application responsiveness."""
    return {"status": "ok"}


# Mount Routers
app.include_router(auth_router)
app.include_router(recommendations_router)
app.include_router(users_router)
app.include_router(items_router)
app.include_router(config_router)
app.include_router(metrics_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
