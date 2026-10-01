from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.incident import Incident, IncidentReport
from backend.app.schemas.common import IncidentResponse, IncidentReportCreate, IncidentReportResponse
from backend.app.agents.orchestrator import orchestrator
from backend.app.core.events import event_manager

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentResponse])
async def list_incidents(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(Incident)
        .options(selectinload(Incident.reports))
        .order_by(Incident.priority_score.desc())
    )
    incidents = stmt.scalars().all()
    return incidents

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(Incident)
        .options(selectinload(Incident.reports))
        .where(Incident.id == incident_id)
    )
    incident = stmt.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/{incident_id}/run-pipeline")
async def run_incident_agent_pipeline(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Triggers the full 7-agent pipeline to formulate and verify an incident response plan."""
    try:
        result = await orchestrator.run_full_pipeline(db, incident_id=incident_id)
        return {"status": "SUCCESS", "pipeline_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")

@router.post("/reports", response_model=IncidentReportResponse)
async def submit_incident_report(report_in: IncidentReportCreate, db: AsyncSession = Depends(get_db)):
    report = IncidentReport(
        source=report_in.source,
        caller_identifier=report_in.caller_identifier,
        raw_text=report_in.raw_text,
        latitude=report_in.latitude or 16.5120,
        longitude=report_in.longitude or 80.6420,
        location_name=report_in.location_name or "Suryanagar Sector 1",
        is_processed=False
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    await event_manager.broadcast("incident.created", {
        "report_id": report.id,
        "raw_text": report.raw_text,
        "source": report.source
    })

    return report
