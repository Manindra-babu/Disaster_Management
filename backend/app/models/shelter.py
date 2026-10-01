import uuid
from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class Shelter(Base, TimestampMixin):
    __tablename__ = "shelters"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    sector: Mapped[str] = mapped_column(String, nullable=False)
    
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    
    total_capacity: Mapped[int] = mapped_column(Integer, default=200)
    current_occupancy: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="OPEN") # OPEN, NEAR_CAPACITY, FULL, CLOSED
    
    has_medical_facility: Mapped[bool] = mapped_column(Boolean, default=True)
    has_power_backup: Mapped[bool] = mapped_column(Boolean, default=True)
    food_days_remaining: Mapped[int] = mapped_column(Integer, default=7)
    water_liters_available: Mapped[int] = mapped_column(Integer, default=10000)
    contact_person: Mapped[str] = mapped_column(String, default="Operations Lead")
    contact_phone: Mapped[str] = mapped_column(String, default="+91-866-555-0100")

    capacity_history = relationship("ShelterCapacity", back_populates="shelter", cascade="all, delete-orphan")

class ShelterCapacity(Base, TimestampMixin):
    __tablename__ = "shelter_capacity"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    shelter_id: Mapped[str] = mapped_column(String, ForeignKey("shelters.id"), nullable=False)
    occupied: Mapped[int] = mapped_column(Integer, nullable=False)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
    available: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    shelter = relationship("Shelter", back_populates="capacity_history")
