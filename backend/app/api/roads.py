import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.road import RoadSegment, RoadCondition, Route
from backend.app.schemas.common import RoadSegmentResponse, RouteResponse

router = APIRouter(prefix="/roads", tags=["Road Network & Routing"])

@router.get("/segments", response_model=List[RoadSegmentResponse])
async def list_road_segments(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(RoadSegment)
        .options(selectinload(RoadSegment.conditions))
        .order_by(RoadSegment.code)
    )
    return stmt.scalars().all()

@router.get("/routes", response_model=List[RouteResponse])
async def list_routes(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Route)
    if status:
        stmt = stmt.where(Route.status == status)
    stmt = stmt.order_by(Route.created_at.desc())
    res = await db.execute(stmt)
    routes = res.scalars().all()
    
    out = []
    for r in routes:
        waypoints = json.loads(r.waypoints_json or "[]")
        out.append(RouteResponse(
            id=r.id,
            incident_id=r.incident_id,
            resource_id=r.resource_id,
            response_plan_id=r.response_plan_id,
            origin_name=r.origin_name,
            destination_name=r.destination_name,
            origin_lat=r.origin_lat,
            origin_lng=r.origin_lng,
            dest_lat=r.dest_lat,
            dest_lng=r.dest_lng,
            total_distance_km=r.total_distance_km,
            estimated_eta_minutes=r.estimated_eta_minutes,
            status=r.status,
            invalidation_reason=r.invalidation_reason,
            waypoints=waypoints,
            is_primary=r.is_primary,
            created_at=r.created_at
        ))
    return out
