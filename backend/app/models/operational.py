import uuid
from typing import Optional
from sqlalchemy import String, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, TimestampMixin

class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String, default="INFO") # CRITICAL, WARNING, INFO, SUCCESS
    category: Mapped[str] = mapped_column(String, default="INCIDENT") # INCIDENT, ROAD_CLOSURE, RESOURCE, WEATHER, DISPATCH, REPLAN
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action: Mapped[str] = mapped_column(String, nullable=False)
    # Actions: INCIDENT_CREATED, TRIAGE_COMPLETED, RESOURCE_ASSIGNED, ROUTE_CALCULATED,
    # SHELTER_ALLOCATED, PLAN_COMPOSED, PLAN_VERIFIED, DISPATCH_APPROVED, DISPATCH_REJECTED,
    # ROUTE_INVALIDATED, REPLANNING_TRIGGERED, SIMULATION_EVENT_TRIGGERED
    
    actor_type: Mapped[str] = mapped_column(String, nullable=False) # AGENT, USER, SYSTEM
    actor_id: Mapped[str] = mapped_column(String, nullable=False) # e.g. "Incident Commander Patel" or "Verification Agent"
    
    target_entity: Mapped[str] = mapped_column(String, nullable=False) # ResponsePlan, Incident, Resource, RoadSegment
    target_id: Mapped[str] = mapped_column(String, nullable=False)
    
    summary: Mapped[str] = mapped_column(String, nullable=False)
    details_json: Mapped[str] = mapped_column(Text, default="{}")
