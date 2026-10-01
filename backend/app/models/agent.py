import uuid
from typing import Optional
from sqlalchemy import String, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimestampMixin

class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_name: Mapped[str] = mapped_column(String, nullable=False) # e.g. "Situation Intelligence Agent"
    scenario_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    response_plan_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    status: Mapped[str] = mapped_column(String, default="RUNNING") # RUNNING, COMPLETED, FAILED, RETRYING
    execution_mode: Mapped[str] = mapped_column(String, default="GEMINI_LLM") # GEMINI_LLM, DETERMINISTIC_ENGINE
    model_name: Mapped[str] = mapped_column(String, default="gemini-2.5-flash")
    
    input_payload_json: Mapped[str] = mapped_column(Text, default="{}")
    input_summary: Mapped[str] = mapped_column(Text, default="")
    structured_output_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    events = relationship("AgentEvent", back_populates="agent_run", cascade="all, delete-orphan")

class AgentEvent(Base, TimestampMixin):
    __tablename__ = "agent_events"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_run_id: Mapped[str] = mapped_column(String, ForeignKey("agent_runs.id"), nullable=False)
    
    event_type: Mapped[str] = mapped_column(String, nullable=False) # TOOL_CALL, TOOL_RESULT, AGENT_STATE, REASONING, ERROR
    tool_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tool_input_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tool_output_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    agent_run = relationship("AgentRun", back_populates="events")
