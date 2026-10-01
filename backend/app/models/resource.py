import uuid
import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Resource(Base, TimestampMixin):
    __tablename__ = "resources"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    callsign: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    resource_type: Mapped[str] = mapped_column(String, nullable=False)
    # Types: AMBULANCE, RESCUE_BOAT, RESCUE_TEAM, FIRE_UNIT, MEDICAL_TEAM, 
    # EVACUATION_BUS, RELIEF_TRUCK, HELICOPTER, GENERATOR, WATER_TANKER, FOOD_SUPPLY_UNIT, MOBILE_MEDICAL_UNIT
    
    capacity: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String, default="AVAILABLE") # AVAILABLE, ASSIGNED, IN_TRANSIT, ON_SCENE, RETURNING, OUT_OF_SERVICE
    
    current_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    current_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    base_station: Mapped[str] = mapped_column(String, nullable=False)
    speed_kmh: Mapped[float] = mapped_column(Float, default=45.0)
    fuel_percent: Mapped[int] = mapped_column(Integer, default=100)
    is_operational: Mapped[bool] = mapped_column(Boolean, default=True)

    assignments = relationship("ResourceAssignment", back_populates="resource")

class ResourceAssignment(Base, TimestampMixin):
    __tablename__ = "resource_assignments"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_id: Mapped[str] = mapped_column(String, ForeignKey("resources.id"), nullable=False)
    incident_id: Mapped[str] = mapped_column(String, ForeignKey("incidents.id"), nullable=False)
    response_plan_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("response_plans.id"), nullable=True)
    status: Mapped[str] = mapped_column(String, default="ASSIGNED") # ASSIGNED, EN_ROUTE, ON_SCENE, RELEASED, CANCELLED
    
    dispatched_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    arrived_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    resource = relationship("Resource", back_populates="assignments")
    response_plan = relationship("ResponsePlan", back_populates="resource_assignments")
