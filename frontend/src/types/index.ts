export type RoleName = 'VIEWER' | 'OPERATOR' | 'INCIDENT_COMMANDER' | 'ADMINISTRATOR';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role_name: RoleName;
  can_approve_dispatch: boolean;
  can_manage_simulations: boolean;
  can_edit_resources: boolean;
}

export interface IncidentReport {
  id: string;
  incident_id?: string;
  source: string;
  caller_identifier?: string;
  raw_text: string;
  extracted_summary?: string;
  latitude?: number;
  longitude?: number;
  location_name?: string;
  is_processed: boolean;
  is_duplicate: boolean;
  created_at: string;
}

export interface Incident {
  id: string;
  title: string;
  description?: string;
  disaster_type: 'flood' | 'cyclone' | 'earthquake' | 'wildfire' | 'landslide' | string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'REPORTED' | 'TRIAGED' | 'IN_PLANNING' | 'DISPATCHED' | 'ACTIVE' | 'RESOLVED';
  latitude: number;
  longitude: number;
  address: string;
  sector: string;
  affected_count: number;
  trapped_count: number;
  medical_critical_count: number;
  priority_score: number;
  triage_rationale?: string;
  is_verified: boolean;
  created_at: string;
  reports?: IncidentReport[];
}

export interface Resource {
  id: string;
  name: string;
  callsign: string;
  resource_type: string;
  capacity: number;
  status: 'AVAILABLE' | 'ASSIGNED' | 'IN_TRANSIT' | 'ON_SCENE' | 'RETURNING' | 'OUT_OF_SERVICE';
  current_latitude: number;
  current_longitude: number;
  base_station: string;
  speed_kmh: number;
  fuel_percent: number;
  is_operational: boolean;
}

export interface ResourceAssignment {
  id: string;
  resource_id: string;
  incident_id: string;
  response_plan_id?: string;
  status: string;
  dispatched_at?: string;
  arrived_at?: string;
  completed_at?: string;
  resource?: Resource;
}

export interface Shelter {
  id: string;
  name: string;
  code: string;
  address: string;
  sector: string;
  latitude: number;
  longitude: number;
  total_capacity: number;
  current_occupancy: number;
  status: 'OPEN' | 'NEAR_CAPACITY' | 'FULL' | 'CLOSED';
  has_medical_facility: boolean;
  has_power_backup: boolean;
  food_days_remaining: number;
  water_liters_available: number;
  contact_person: string;
  contact_phone: string;
}

export interface RoadCondition {
  id: string;
  road_segment_id: string;
  status: string;
  is_blocked: boolean;
  hazard_severity: number;
  water_depth_cm: number;
  obstruction_details?: string;
  passable_for_boat: boolean;
  passable_for_high_clearance: boolean;
}

export interface RoadSegment {
  id: string;
  name: string;
  code: string;
  road_type: string;
  start_lat: number;
  start_lng: number;
  end_lat: number;
  end_lng: number;
  length_km: number;
  speed_limit_kmh: number;
  conditions: RoadCondition[];
}

export interface Route {
  id: string;
  incident_id?: string;
  resource_id?: string;
  response_plan_id?: string;
  origin_name: string;
  destination_name: string;
  origin_lat: number;
  origin_lng: number;
  dest_lat: number;
  dest_lng: number;
  total_distance_km: number;
  estimated_eta_minutes: number;
  status: 'ACTIVE' | 'INVALIDATED' | 'COMPLETED' | 'REROUTED';
  invalidation_reason?: string;
  waypoints: [number, number][];
  is_primary: boolean;
}

export interface ResponsePlan {
  id: string;
  incident_id: string;
  target_shelter_id?: string;
  title: string;
  summary: string;
  status: 'DRAFT' | 'VERIFIED' | 'AWAITING_APPROVAL' | 'APPROVED' | 'DISPATCHED' | 'IN_TRANSIT' | 'ARRIVED' | 'COMPLETED' | 'REPLANNING' | 'REJECTED';
  version: number;
  is_verified: boolean;
  verification_score?: number;
  verification_notes?: string;
  approved_by_user_id?: string;
  approved_at?: string;
  approval_notes?: string;
  is_invalidated: boolean;
  invalidation_reason?: string;
  superseded_by_plan_id?: string;
  created_at: string;
  resource_assignments: ResourceAssignment[];
  target_shelter?: Shelter;
  routes?: Route[];
}

export interface AgentEvent {
  id: string;
  agent_run_id: string;
  event_type: string;
  tool_name?: string;
  message: string;
  created_at: string;
}

export interface AgentRun {
  id: string;
  agent_name: string;
  scenario_id?: string;
  incident_id?: string;
  response_plan_id?: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  execution_mode: 'GEMINI_LLM' | 'DETERMINISTIC_ENGINE';
  model_name: string;
  input_summary: string;
  structured_output_json?: string;
  decision_explanation?: string;
  duration_ms: number;
  retry_count: number;
  error_message?: string;
  tokens_used: number;
  created_at: string;
  events?: AgentEvent[];
}

export interface AgentDefinition {
  id: string;
  name: string;
  role: string;
  description: string;
  tools: string[];
  input_types: string[];
  output_types: string[];
}

export interface SimulationEvent {
  id: string;
  scenario_id: string;
  tick: number;
  event_type: string;
  title: string;
  description: string;
  payload_json: string;
  is_executed: boolean;
}

export interface SimulationScenario {
  id: string;
  name: string;
  disaster_type: string;
  location_name: string;
  description: string;
  status: 'IDLE' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'RESET';
  current_tick: number;
  speed_multiplier: number;
  seed: number;
  weather_summary: string;
  wind_speed_kmh: number;
  rainfall_mm: number;
  events: SimulationEvent[];
}

export interface Alert {
  id: string;
  title: string;
  message: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO' | 'SUCCESS';
  category: string;
  latitude?: number;
  longitude?: number;
  is_acknowledged: boolean;
  created_at: string;
}

export interface AuditLog {
  id: string;
  action: string;
  actor_type: string;
  actor_id: string;
  target_entity: string;
  target_id: string;
  summary: string;
  details_json: string;
  created_at: string;
}

export interface OperationalKPIs {
  active_incidents: number;
  critical_incidents: number;
  people_affected: number;
  people_trapped: number;
  medical_critical: number;
  available_resources: number;
  deployed_resources: number;
  total_resources: number;
  shelter_occupancy: number;
  shelter_total_capacity: number;
  shelter_occupancy_pct: number;
}
