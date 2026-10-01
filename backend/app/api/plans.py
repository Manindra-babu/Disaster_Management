import datetime
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.response_plan import ResponsePlan
from backend.app.models.resource import Resource, ResourceAssignment
from backend.app.models.user import User
from backend.app.models.operational import AuditLog, Alert
from backend.app.schemas.common import ResponsePlanResponse, PlanApprovalRequest
from backend.app.api.deps import require_incident_commander, get_current_user
from backend.app.core.events import event_manager

router = APIRouter(prefix="/plans", tags=["Response Plans"])

@router.get("", response_model=List[ResponsePlanResponse])
async def list_plans(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(ResponsePlan)
        .options(
            selectinload(ResponsePlan.resource_assignments).selectinload(ResourceAssignment.resource),
            selectinload(ResponsePlan.target_shelter)
        )
        .order_by(ResponsePlan.created_at.desc())
    )
    return stmt.scalars().all()

@router.get("/{plan_id}", response_model=ResponsePlanResponse)
async def get_plan(plan_id: str, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(ResponsePlan)
        .options(
            selectinload(ResponsePlan.resource_assignments).selectinload(ResourceAssignment.resource),
            selectinload(ResponsePlan.target_shelter)
        )
        .where(ResponsePlan.id == plan_id)
    )
    plan = stmt.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Response plan not found")
    return plan

@router.post("/{plan_id}/approve", response_model=ResponsePlanResponse)
async def approve_and_dispatch_plan(
    plan_id: str,
    req: PlanApprovalRequest,
    current_user: User = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db)
):
    """
    Authoritative dispatch approval.
    STRICT SECURITY REQUIREMENT: Only Incident Commanders may execute dispatch approval.
    Transitions plan status to APPROVED -> DISPATCHED, updates resources to IN_TRANSIT,
    records immutable audit log, and publishes real-time WebSocket events.
    """
    stmt = await db.execute(
        select(ResponsePlan)
        .options(
            selectinload(ResponsePlan.resource_assignments).selectinload(ResourceAssignment.resource),
            selectinload(ResponsePlan.target_shelter)
        )
        .where(ResponsePlan.id == plan_id)
    )
    plan = stmt.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Response plan not found")

    if not plan.is_verified:
        raise HTTPException(status_code=400, detail="Cannot dispatch unverified plan. Verification checks must pass.")

    # State transition
    plan.status = "DISPATCHED"
    plan.approved_by_user_id = current_user.id
    plan.approved_at = datetime.datetime.now(datetime.timezone.utc)
    plan.approval_notes = req.notes or f"Approved for dispatch by {current_user.full_name} ({current_user.role.name if current_user.role else 'INCIDENT_COMMANDER'})"

    # Update assigned resources to IN_TRANSIT
    for asgn in plan.resource_assignments:
        asgn.status = "EN_ROUTE"
        asgn.dispatched_at = plan.approved_at
        await db.execute(
            update(Resource)
            .where(Resource.id == asgn.resource_id)
            .values(status="IN_TRANSIT")
        )

    # Immutable Audit Log
    audit = AuditLog(
        action="DISPATCH_APPROVED",
        actor_type="USER",
        actor_id=f"{current_user.full_name} ({current_user.role.name if current_user.role else 'Commander'})",
        target_entity="ResponsePlan",
        target_id=plan.id,
        summary=f"Incident Commander approved immediate operational dispatch for plan: {plan.title}.",
        details_json=json.dumps({
            "commander_id": current_user.id,
            "commander_email": current_user.email,
            "resources_dispatched": [a.resource.callsign for a in plan.resource_assignments if a.resource],
            "notes": plan.approval_notes
        })
    )
    db.add(audit)

    # Alert Notification
    alert = Alert(
        title=f"Emergency Dispatch Authorized: {plan.title}",
        message=f"{len(plan.resource_assignments)} response units have mobilized and are currently EN ROUTE.",
        severity="SUCCESS",
        category="DISPATCH"
    )
    db.add(alert)

    await db.commit()
    await db.refresh(plan)

    # Broadcast WebSocket events
    await event_manager.broadcast("dispatch.approved", {
        "plan_id": plan.id,
        "title": plan.title,
        "commander": current_user.full_name,
        "status": "DISPATCHED",
        "units": [a.resource.callsign for a in plan.resource_assignments if a.resource]
    })

    return plan

@router.post("/{plan_id}/reject", response_model=ResponsePlanResponse)
async def reject_plan(
    plan_id: str,
    req: PlanApprovalRequest,
    current_user: User = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db)
):
    stmt = await db.execute(select(ResponsePlan).where(ResponsePlan.id == plan_id))
    plan = stmt.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Response plan not found")

    plan.status = "REJECTED"
    plan.approval_notes = req.notes or "Plan rejected by Incident Commander"
    
    # Release assigned resources
    for asgn in plan.resource_assignments:
        asgn.status = "CANCELLED"
        await db.execute(update(Resource).where(Resource.id == asgn.resource_id).values(status="AVAILABLE"))

    await db.commit()
    await db.refresh(plan)
    return plan
