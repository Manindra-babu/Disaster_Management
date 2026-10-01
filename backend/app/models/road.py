import uuid
from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class RoadSegment(Base, TimestampMixin):
    __tablename__ = "road_segments"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    road_type: Mapped[str] = mapped_column(String, default="ARTERIAL") # HIGHWAY, ARTERIAL, LOCAL, BRIDGE, GHAT_ROAD
    start_node: Mapped[str] = mapped_column(String, default="SEC-1")
    end_node: Mapped[str] = mapped_column(String, default="SEC-3")
    
    start_lat: Mapped[float] = mapped_column(Float, nullable=False)
    start_lng: Mapped[float] = mapped_column(Float, nullable=False)
    end_lat: Mapped[float] = mapped_column(Float, nullable=False)
    end_lng: Mapped[float] = mapped_column(Float, nullable=False)
    
    length_km: Mapped[float] = mapped_column(Float, default=1.0)
    speed_limit_kmh: Mapped[float] = mapped_column(Float, default=50.0)

    conditions = relationship("RoadCondition", back_populates="road_segment", cascade="all, delete-orphan")

class RoadCondition(Base, TimestampMixin):
    __tablename__ = "road_conditions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    road_segment_id: Mapped[str] = mapped_column(String, ForeignKey("road_segments.id"), nullable=False)
    
    status: Mapped[str] = mapped_column(String, default="CLEAR") # CLEAR, FLOODED, DEBRIS_BLOCKED, BRIDGE_COLLAPSE, FIRE_CORRIDOR, LANDSLIDE_BLOCKED
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    hazard_severity: Mapped[int] = mapped_column(Integer, default=0) # 0 to 10
    water_depth_cm: Mapped[int] = mapped_column(Integer, default=0)
    obstruction_details: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    passable_for_boat: Mapped[bool] = mapped_column(Boolean, default=False)
    passable_for_high_clearance: Mapped[bool] = mapped_column(Boolean, default=True)

    road_segment = relationship("RoadSegment", back_populates="conditions")

class Route(Base, TimestampMixin):
    __tablename__ = "routes"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("incidents.id"), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("resources.id"), nullable=True)
    response_plan_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("response_plans.id"), nullable=True)
    
    origin_name: Mapped[str] = mapped_column(String, nullable=False)
    destination_name: Mapped[str] = mapped_column(String, nullable=False)
    origin_lat: Mapped[float] = mapped_column(Float, nullable=False)
    origin_lng: Mapped[float] = mapped_column(Float, nullable=False)
    dest_lat: Mapped[float] = mapped_column(Float, nullable=False)
    dest_lng: Mapped[float] = mapped_column(Float, nullable=False)
    
    total_distance_km: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_eta_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    
    status: Mapped[str] = mapped_column(String, default="ACTIVE") # ACTIVE, INVALIDATED, COMPLETED, REROUTED
    invalidation_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    waypoints_json: Mapped[str] = mapped_column(Text, default="[]") # JSON list of [lat, lng]
    segments_traversed_json: Mapped[str] = mapped_column(Text, default="[]") # JSON list of segment ids
    
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
