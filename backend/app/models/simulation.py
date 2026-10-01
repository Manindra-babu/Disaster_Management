import uuid
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class SimulationScenario(Base, TimestampMixin):
    __tablename__ = "simulation_scenarios"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    disaster_type: Mapped[str] = mapped_column(String, nullable=False) # flood, cyclone, earthquake, wildfire, landslide
    location_name: Mapped[str] = mapped_column(String, default="Suryanagar, India")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    status: Mapped[str] = mapped_column(String, default="IDLE") # IDLE, RUNNING, PAUSED, COMPLETED, RESET
    current_tick: Mapped[int] = mapped_column(Integer, default=0)
    speed_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    seed: Mapped[int] = mapped_column(Integer, default=42)
    
    weather_summary: Mapped[str] = mapped_column(String, default="Severe weather conditions active")
    wind_speed_kmh: Mapped[float] = mapped_column(Float, default=30.0)
    rainfall_mm: Mapped[float] = mapped_column(Float, default=0.0)
    
    events = relationship("SimulationEvent", back_populates="scenario", cascade="all, delete-orphan")

class SimulationEvent(Base, TimestampMixin):
    __tablename__ = "simulation_events"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id: Mapped[str] = mapped_column(String, ForeignKey("simulation_scenarios.id"), nullable=False)
    
    tick: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False) 
    # INCIDENT_REPORT, ROAD_BLOCKAGE, SHELTER_SPIKE, WEATHER_ESCALATION, HAZARD_EXPANSION
    
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    is_executed: Mapped[bool] = mapped_column(Boolean, default=False)

    scenario = relationship("SimulationScenario", back_populates="events")
