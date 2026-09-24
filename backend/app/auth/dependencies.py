from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_async_db
from app.models.db_models import Admin
from app.models.schemas import TokenData
from app.auth.security import decode_access_token

security_scheme = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> Admin:
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
    if username is None or role != "admin":
        raise credentials_exception

    stmt = select(Admin).where(Admin.username == username)
    result = await db.execute(stmt)
    admin = result.scalar_one_or_none()
    if admin is None:
        raise credentials_exception
    return admin
