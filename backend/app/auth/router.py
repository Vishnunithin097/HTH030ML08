"""
Authentication API Router.
Handles Admin JWT authentication.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.models.db_models import Admin
from app.models.schemas import AdminLogin, TokenResponse
from app.auth.security import verify_password, create_access_token, get_password_hash
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: AdminLogin, db: AsyncSession = Depends(get_async_db)):
    """
    Authenticates Admin user with username and password, returning a JWT bearer token.
    """
    admin = None
    try:
        stmt = select(Admin).where(Admin.username == payload.username)
        result = db.execute(stmt)
        admin = result.scalar_one_or_none()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Database admin lookup failed during auth: {e}")

    # Validate against DB or fallback default admin credentials for local dev
    is_valid = False
    if admin:
        is_valid = verify_password(payload.password, admin.hashed_password)
    elif settings.ENVIRONMENT.lower() != "production" and payload.username == "admin" and payload.password == "Admin@123":
        is_valid = True

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": payload.username, "role": "admin"},
        expires_delta=access_token_expires,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=payload.username,
        role="admin",
    )
