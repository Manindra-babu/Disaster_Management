import uuid
from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("simulation_scenarios.id"), nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    disaster_type: Mapped[str] = mapped_column(String, nullable=False)  # flood, cyclone, earthquake, wildfire, landslide
    severity: Mapped[str] = mapped_column(String, default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    status: Mapped[str] = mapped_column(String, default="REPORTED")  # REPORTED, TRIAGED, IN_PLANNING, DISPATCHED, ACTIVE, RESOLVED
    
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    sector: Mapped[str] = mapped_column(String, nullable=False)
    
    affected_count: Mapped[int] = mapped_column(Integer, default=0)
    trapped_count: Mapped[int] = mapped_column(Integer, default=0)
    medical_critical_count: Mapped[int] = mapped_column(Integer, default=0)
    
    priority_score: Mapped[float] = mapped_column(Float, default=50.0)
    triage_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    reports = relationship("IncidentReport", back_populates="incident", cascade="all, delete-orphan")
    response_plans = relationship("ResponsePlan", back_populates="incident")

class IncidentReport(Base, TimestampMixin):
    __tablename__ = "incident_reports"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("incidents.id"), nullable=True)
    source: Mapped[str] = mapped_column(String, default="EMERGENCY_CALL")  # EMERGENCY_CALL, CITIZEN_SMS, FIELD_OPERATOR, SENSOR_TELEMETRY
    caller_identifier: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_of_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("incident_reports.id"), nullable=True)
    
    incident = relationship("Incident", back_populates="reports")
