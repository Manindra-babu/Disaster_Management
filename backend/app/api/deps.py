from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.user import User, Role

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user_optional(
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not token_auth:
        # Default to demo commander if not logged in to make demo completely seamless
        stmt = await db.execute(
            select(User)
            .options(joinedload(User.role))
            .join(User.role)
            .where(Role.name == "INCIDENT_COMMANDER")
        )
        return stmt.scalars().first()

    payload = decode_access_token(token_auth.credentials)
    if not payload:
        return None

    user_id = payload.get("sub")
    stmt = await db.execute(
        select(User)
        .options(joinedload(User.role))
        .where(User.id == user_id)
    )
    return stmt.scalar_one_or_none()

async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or have expired."
        )
    return user

async def require_incident_commander(
    user: User = Depends(get_current_user)
) -> User:
    if not user.role or not user.role.can_approve_dispatch:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only authorized Incident Commanders may approve emergency dispatch."
        )
    return user
