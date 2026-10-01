from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

from backend.app.core.database import get_db
from backend.app.core.security import verify_password, create_access_token
from backend.app.models.user import User, Role
from backend.app.schemas.common import UserLogin, TokenResponse, UserResponse
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RoleSwitchRequest(BaseModel):
    role_name: str # VIEWER, OPERATOR, INCIDENT_COMMANDER, ADMINISTRATOR

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(User)
        .options(joinedload(User.role))
        .where(User.email == credentials.email)
    )
    user = stmt.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    token = create_access_token(
        subject=user.id,
        role_name=user.role.name,
        can_approve_dispatch=user.role.can_approve_dispatch
    )
    
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role_name=user.role.name,
        can_approve_dispatch=user.role.can_approve_dispatch,
        can_manage_simulations=user.role.can_manage_simulations,
        can_edit_resources=user.role.can_edit_resources
    )
    
    return TokenResponse(access_token=token, user=user_resp)

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role_name=user.role.name if user.role else "OPERATOR",
        can_approve_dispatch=user.role.can_approve_dispatch if user.role else True,
        can_manage_simulations=user.role.can_manage_simulations if user.role else True,
        can_edit_resources=user.role.can_edit_resources if user.role else True
    )

@router.get("/users", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(User).options(joinedload(User.role)))
    users = stmt.scalars().all()
    return [
        UserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role_name=u.role.name,
            can_approve_dispatch=u.role.can_approve_dispatch,
            can_manage_simulations=u.role.can_manage_simulations,
            can_edit_resources=u.role.can_edit_resources
        )
        for u in users
    ]

@router.post("/switch-demo-role", response_model=TokenResponse)
async def switch_demo_role(req: RoleSwitchRequest, db: AsyncSession = Depends(get_db)):
    """Convenience endpoint for evaluators to test role permissions between Commander, Operator and Viewer."""
    r_stmt = await db.execute(select(Role).where(Role.name == req.role_name))
    role = r_stmt.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=400, detail=f"Role {req.role_name} not recognized.")
        
    u_stmt = await db.execute(select(User).where(User.role_id == role.id))
    user = u_stmt.scalars().first()
    if not user:
        user = User(
            email=f"{req.role_name.lower()}@resq.gov.in",
            full_name=f"Demo {req.role_name.capitalize()}",
            hashed_password="demo",
            role_id=role.id
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_access_token(
        subject=user.id,
        role_name=role.name,
        can_approve_dispatch=role.can_approve_dispatch
    )
    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role_name=role.name,
        can_approve_dispatch=role.can_approve_dispatch,
        can_manage_simulations=role.can_manage_simulations,
        can_edit_resources=role.can_edit_resources
    )
    return TokenResponse(access_token=token, user=user_resp)
