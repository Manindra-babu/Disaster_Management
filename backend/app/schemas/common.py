import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

# User Schemas
class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role_name: str
    can_approve_dispatch: bool
    can_manage_simulations: bool
    can_edit_resources: bool
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Incident Schemas
class IncidentReportCreate(BaseModel):
    raw_text: str
    source: str = "EMERGENCY_CALL"
    caller_identifier: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None

class IncidentReportResponse(BaseModel):
    id: str
    incident_id: Optional[str]
    source: str
    caller_identifier: Optional[str]
    raw_text: str
    extracted_summary: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    location_name: Optional[str]
    is_processed: bool
    is_duplicate: bool
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class IncidentResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    disaster_type: str
    severity: str
    status: str
    latitude: float
    longitude: float
    address: str
    sector: str
    affected_count: int
    trapped_count: int
    medical_critical_count: int
    priority_score: float
    triage_rationale: Optional[str]
    is_verified: bool
    created_at: datetime.datetime
    reports: List[IncidentReportResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Resource Schemas
class ResourceResponse(BaseModel):
    id: str
    name: str
    callsign: str
    resource_type: str
    capacity: int
    status: str
    current_latitude: float
    current_longitude: float
    base_station: str
    speed_kmh: float
    fuel_percent: int
    is_operational: bool
    model_config = ConfigDict(from_attributes=True)

class ResourceAssignmentResponse(BaseModel):
    id: str
    resource_id: str
    incident_id: str
    response_plan_id: Optional[str]
    status: str
    dispatched_at: Optional[datetime.datetime]
    arrived_at: Optional[datetime.datetime]
    completed_at: Optional[datetime.datetime]
    resource: Optional[ResourceResponse] = None
    model_config = ConfigDict(from_attributes=True)

# Shelter Schemas
class ShelterResponse(BaseModel):
    id: str
    name: str
    code: str
    address: str
    sector: str
    latitude: float
    longitude: float
    total_capacity: int
    current_occupancy: int
    status: str
    has_medical_facility: bool
    has_power_backup: bool
    food_days_remaining: int
    water_liters_available: int
    contact_person: str
    contact_phone: str
    model_config = ConfigDict(from_attributes=True)

# Road & Route Schemas
class RoadConditionResponse(BaseModel):
    id: str
    road_segment_id: str
    status: str
    is_blocked: bool
    hazard_severity: int
    water_depth_cm: int
    obstruction_details: Optional[str]
    passable_for_boat: bool
    passable_for_high_clearance: bool
    model_config = ConfigDict(from_attributes=True)

class RoadSegmentResponse(BaseModel):
    id: str
    name: str
    code: str
    road_type: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    length_km: float
    speed_limit_kmh: float
    conditions: List[RoadConditionResponse] = []
    model_config = ConfigDict(from_attributes=True)

class RouteResponse(BaseModel):
    id: str
    incident_id: Optional[str]
    resource_id: Optional[str]
    response_plan_id: Optional[str]
    origin_name: str
    destination_name: str
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    total_distance_km: float
    estimated_eta_minutes: float
    status: str
    invalidation_reason: Optional[str]
    waypoints: List[List[float]] = [] # parsed from waypoints_json
    is_primary: bool
    model_config = ConfigDict(from_attributes=True)

# Response Plan Schemas
class ResponsePlanResponse(BaseModel):
    id: str
    incident_id: str
    target_shelter_id: Optional[str]
    title: str
    summary: str
    status: str
    version: int
    is_verified: bool
    verification_score: Optional[int]
    verification_notes: Optional[str]
    approved_by_user_id: Optional[str]
    approved_at: Optional[datetime.datetime]
    approval_notes: Optional[str]
    is_invalidated: bool
    invalidation_reason: Optional[str]
    superseded_by_plan_id: Optional[str]
    created_at: datetime.datetime
    resource_assignments: List[ResourceAssignmentResponse] = []
    target_shelter: Optional[ShelterResponse] = None
    routes: List[RouteResponse] = []
    model_config = ConfigDict(from_attributes=True)

class PlanApprovalRequest(BaseModel):
    notes: Optional[str] = "Approved by Incident Commander for immediate dispatch."

# Agent Schemas
class AgentEventResponse(BaseModel):
    id: str
    agent_run_id: str
    event_type: str
    tool_name: Optional[str]
    tool_input_json: Optional[str]
    tool_output_json: Optional[str]
    message: str
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class AgentRunResponse(BaseModel):
    id: str
    agent_name: str
    scenario_id: Optional[str]
    incident_id: Optional[str]
    response_plan_id: Optional[str]
    status: str
    execution_mode: str
    model_name: str
    input_summary: str
    structured_output_json: Optional[str]
    decision_explanation: Optional[str]
    duration_ms: float
    retry_count: int
    error_message: Optional[str]
    tokens_used: int
    created_at: datetime.datetime
    events: List[AgentEventResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Simulation Schemas
class SimulationEventResponse(BaseModel):
    id: str
    scenario_id: str
    tick: int
    event_type: str
    title: str
    description: str
    payload_json: str
    is_executed: bool
    model_config = ConfigDict(from_attributes=True)

class SimulationScenarioResponse(BaseModel):
    id: str
    name: str
    disaster_type: str
    location_name: str
    description: str
    status: str
    current_tick: int
    speed_multiplier: float
    seed: int
    weather_summary: str
    wind_speed_kmh: float
    rainfall_mm: float
    events: List[SimulationEventResponse] = []
    model_config = ConfigDict(from_attributes=True)

class HazardInjectionRequest(BaseModel):
    segment_code: str
    blockage_type: str = "DEBRIS_BLOCKED" # FLOODED, DEBRIS_BLOCKED, BRIDGE_COLLAPSE, LANDSLIDE_BLOCKED
    description: str = "Unscheduled obstruction detected on key transit arterial."

# Operational Schemas
class AlertResponse(BaseModel):
    id: str
    title: str
    message: str
    severity: str
    category: str
    latitude: Optional[float]
    longitude: Optional[float]
    is_acknowledged: bool
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class AuditLogResponse(BaseModel):
    id: str
    action: str
    actor_type: str
    actor_id: str
    target_entity: str
    target_id: str
    summary: str
    details_json: str
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)
