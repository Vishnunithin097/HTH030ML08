"""
Authentication Dependencies.
Protects Admin endpoints with JWT verification.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.models.db_models import Admin
from app.auth.security import decode_access_token

security_scheme = HTTPBearer(auto_error=True)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> dict:
    """
    Validates JWT token and asserts admin role authorization.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    role: str = payload.get("role")
    if not username or role != "admin":
        raise credentials_exception

    return {"username": username, "role": role}
