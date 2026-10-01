import uuid
import datetime
from typing import Optional
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class ResponsePlan(Base, TimestampMixin):
    __tablename__ = "response_plans"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[str] = mapped_column(String, ForeignKey("incidents.id"), nullable=False)
    target_shelter_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("shelters.id"), nullable=True)
    
    title: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Lifecycle: DRAFT -> VERIFIED -> AWAITING_APPROVAL -> APPROVED -> DISPATCHED -> IN_TRANSIT -> ARRIVED -> COMPLETED (or REPLANNING / REJECTED)
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Verification details
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_score: Mapped[Optional[int]] = mapped_column(Integer, default=0) # 0 to 100
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Human Dispatch Approval details (Only INCIDENT_COMMANDER can approve)
    approved_by_user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Invalidation & Replanning trigger
    is_invalidated: Mapped[bool] = mapped_column(Boolean, default=False)
    invalidation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    superseded_by_plan_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    incident = relationship("Incident", back_populates="response_plans")
    resource_assignments = relationship("ResourceAssignment", back_populates="response_plan", cascade="all, delete-orphan")
    target_shelter = relationship("Shelter")
    approved_by = relationship("User")
