from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.agent import AgentRun, AgentEvent
from backend.app.schemas.common import AgentRunResponse

router = APIRouter(prefix="/agents", tags=["Agent Observatory"])

SEVEN_AGENTS = [
    {
        "id": "agent-situation",
        "name": "Situation Intelligence Agent",
        "role": "Ingestion & De-duplication",
        "description": "Parses multi-source emergency calls, removes duplicate reports, extracts trapped and medical figures.",
        "tools": ["search_existing_reports", "compute_text_similarity", "extract_geocodes"],
        "input_types": ["Emergency Call Audio/Text", "Citizen SMS", "Sensor Alerts"],
        "output_types": ["Structured Incident Parameters", "Duplicate Groupings"]
    },
    {
        "id": "agent-triage",
        "name": "Triage and Priority Agent",
        "role": "Deterministic Priority & Urgency",
        "description": "Calculates life-threat priority score (0-100), urgency window, and recommends required capability profiles.",
        "tools": ["calculate_priority_score", "evaluate_urgency_window"],
        "input_types": ["Structured Incident Parameters"],
        "output_types": ["Priority Score", "Severity Level", "Capability Requirements"]
    },
    {
        "id": "agent-resource",
        "name": "Resource Allocation Agent",
        "role": "Fleet Assignment & Non-Conflict",
        "description": "Inspects operational inventory, matches capability, minimizes distance, and strictly prevents double-booking.",
        "tools": ["get_available_resources", "check_resource_status", "reserve_resource"],
        "input_types": ["Capability Requirements", "Incident Coordinates"],
        "output_types": ["Assigned Unit List", "Travel Time Estimates"]
    },
    {
        "id": "agent-route",
        "name": "Route Optimization Agent",
        "role": "Graph Routing & Closure Avoidance",
        "description": "Calculates shortest paths via Suryanagar graph, checks hazard zones, evaluates closure bypasses and computes ETAs.",
        "tools": ["query_road_graph", "check_closure_status", "calculate_path"],
        "input_types": ["Unit Base Stations", "Incident & Shelter Waypoints"],
        "output_types": ["Primary Polyline", "Alternative Corridors", "ETA"]
    },
    {
        "id": "agent-shelter",
        "name": "Shelter and Capacity Agent",
        "role": "Evacuation Headroom & Medical Matching",
        "description": "Audits real-time shelter occupancy, matches casualty requirements with clinical facilities, reserves capacity.",
        "tools": ["get_shelter_capacities", "reserve_shelter_capacity"],
        "input_types": ["Evacuee Headcount", "Medical Acuity Flag"],
        "output_types": ["Designated Shelter", "Remaining Bed Buffer"]
    },
    {
        "id": "agent-coordination",
        "name": "Coordination Agent",
        "role": "Response Plan Synthesis",
        "description": "Synthesizes intelligence, triage, units, routes, and shelter into a phased, versioned operational response plan.",
        "tools": ["compose_response_plan", "format_commander_briefing"],
        "input_types": ["All Upstream Agent Outputs"],
        "output_types": ["Unified Response Plan (v1)"]
    },
    {
        "id": "agent-verification",
        "name": "Verification Agent",
        "role": "Independent Ground-Truth Auditor",
        "description": "Conducts adversarial audit: verifies zero double-bookings, confirms zero closure overlap, checks headroom buffer.",
        "tools": ["audit_resource_conflicts", "audit_road_clearance", "audit_shelter_headroom"],
        "input_types": ["Proposed Response Plan", "Authoritative DB State"],
        "output_types": ["Verification Score", "Commander Safety Checklist", "Approval Recommendation"]
    }
]

@router.get("/definitions")
async def get_agent_definitions():
    """Returns static architecture schemas and capabilities of the 7 specialized agents."""
    return SEVEN_AGENTS

@router.get("/runs", response_model=List[AgentRunResponse])
async def list_agent_runs(limit: int = 50, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(AgentRun)
        .options(selectinload(AgentRun.events))
        .order_by(AgentRun.created_at.desc())
        .limit(limit)
    )
    return stmt.scalars().all()

@router.get("/runs/{run_id}", response_model=AgentRunResponse)
async def get_agent_run(run_id: str, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(AgentRun)
        .options(selectinload(AgentRun.events))
        .where(AgentRun.id == run_id)
    )
    run = stmt.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return run
