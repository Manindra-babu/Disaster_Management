from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.core.database import get_db
from backend.app.models.incident import Incident
from backend.app.models.resource import Resource
from backend.app.models.shelter import Shelter
from backend.app.models.operational import Alert, AuditLog
from backend.app.schemas.common import AlertResponse, AuditLogResponse

router = APIRouter(prefix="/operational", tags=["Operational Intelligence & KPIs"])

@router.get("/kpis")
async def get_operational_kpis(db: AsyncSession = Depends(get_db)):
    """
    Every displayed metric must derive from actual database or simulation state!
    KPIs:
    - active incidents
    - critical incidents
    - people affected
    - available resources
    - deployed resources
    - shelter occupancy / capacity
    """
    # Active incidents
    inc_stmt = await db.execute(select(Incident))
    all_incidents = inc_stmt.scalars().all()
    active_incidents = [i for i in all_incidents if i.status != "RESOLVED"]
    critical_incidents = [i for i in active_incidents if i.severity == "CRITICAL"]
    people_affected = sum(i.affected_count for i in active_incidents)
    people_trapped = sum(i.trapped_count for i in active_incidents)
    medical_critical = sum(i.medical_critical_count for i in active_incidents)

    # Resources
    res_stmt = await db.execute(select(Resource))
    all_resources = res_stmt.scalars().all()
    available_resources = sum(1 for r in all_resources if r.status == "AVAILABLE")
    deployed_resources = sum(1 for r in all_resources if r.status in ["ASSIGNED", "IN_TRANSIT", "ON_SCENE"])
    total_resources = len(all_resources)

    # Shelters
    sh_stmt = await db.execute(select(Shelter))
    all_shelters = sh_stmt.scalars().all()
    total_capacity = sum(s.total_capacity for s in all_shelters)
    current_occupancy = sum(s.current_occupancy for s in all_shelters)
    occupancy_pct = round((current_occupancy / max(1, total_capacity)) * 100, 1)

    return {
        "active_incidents": len(active_incidents),
        "critical_incidents": len(critical_incidents),
        "people_affected": people_affected,
        "people_trapped": people_trapped,
        "medical_critical": medical_critical,
        "available_resources": available_resources,
        "deployed_resources": deployed_resources,
        "total_resources": total_resources,
        "shelter_occupancy": current_occupancy,
        "shelter_total_capacity": total_capacity,
        "shelter_occupancy_pct": occupancy_pct
    }

@router.get("/alerts", response_model=List[AlertResponse])
async def list_alerts(limit: int = 40, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(Alert)
        .order_by(Alert.created_at.desc())
        .limit(limit)
    )
    return stmt.scalars().all()

@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = stmt.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_acknowledged = True
    await db.commit()
    await db.refresh(alert)
    return alert

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(limit: int = 60, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    return stmt.scalars().all()
