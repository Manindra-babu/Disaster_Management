from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from backend.app.core.database import get_db
from backend.app.models.resource import Resource
from backend.app.schemas.common import ResourceResponse
from backend.app.core.events import event_manager

router = APIRouter(prefix="/resources", tags=["Resources"])

class StatusUpdateRequest(BaseModel):
    status: str # AVAILABLE, ASSIGNED, IN_TRANSIT, ON_SCENE, RETURNING, OUT_OF_SERVICE

@router.get("", response_model=List[ResourceResponse])
async def list_resources(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Resource)
    if status:
        stmt = stmt.where(Resource.status == status)
    stmt = stmt.order_by(Resource.resource_type, Resource.callsign)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: str, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = stmt.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.patch("/{resource_id}/status", response_model=ResourceResponse)
async def update_resource_status(resource_id: str, req: StatusUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = stmt.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    resource.status = req.status
    await db.commit()
    await db.refresh(resource)

    await event_manager.broadcast("resource.updated", {
        "resource_id": resource.id,
        "callsign": resource.callsign,
        "status": resource.status
    })

    return resource
