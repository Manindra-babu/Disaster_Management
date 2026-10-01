from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from backend.app.core.database import get_db
from backend.app.models.shelter import Shelter, ShelterCapacity
from backend.app.schemas.common import ShelterResponse
from backend.app.core.events import event_manager

router = APIRouter(prefix="/shelters", tags=["Shelters"])

class OccupancyUpdateRequest(BaseModel):
    intake_count: int

@router.get("", response_model=List[ShelterResponse])
async def list_shelters(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Shelter).order_by(Shelter.total_capacity.desc()))
    return stmt.scalars().all()

@router.get("/{shelter_id}", response_model=ShelterResponse)
async def get_shelter(shelter_id: str, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Shelter).where(Shelter.id == shelter_id))
    shelter = stmt.scalar_one_or_none()
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found")
    return shelter

@router.post("/{shelter_id}/intake", response_model=ShelterResponse)
async def record_intake(shelter_id: str, req: OccupancyUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Shelter).where(Shelter.id == shelter_id))
    shelter = stmt.scalar_one_or_none()
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found")

    shelter.current_occupancy = min(shelter.total_capacity, shelter.current_occupancy + req.intake_count)
    if shelter.current_occupancy >= shelter.total_capacity:
        shelter.status = "FULL"
    elif shelter.current_occupancy >= (shelter.total_capacity * 0.85):
        shelter.status = "NEAR_CAPACITY"

    # Record capacity event
    cap_log = ShelterCapacity(
        shelter_id=shelter.id,
        occupied=shelter.current_occupancy,
        available=shelter.total_capacity - shelter.current_occupancy,
        note=f"Admitted {req.intake_count} evacuees"
    )
    db.add(cap_log)
    await db.commit()
    await db.refresh(shelter)

    await event_manager.broadcast("shelter.updated", {
        "shelter_id": shelter.id,
        "name": shelter.name,
        "occupancy": shelter.current_occupancy,
        "total_capacity": shelter.total_capacity,
        "status": shelter.status
    })

    return shelter
