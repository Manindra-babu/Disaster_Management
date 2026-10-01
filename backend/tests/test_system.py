import json
import asyncio
import pytest
from backend.app.core.database import init_db, AsyncSessionLocal
from backend.app.models.user import User, Role
from backend.app.models.incident import Incident
from backend.app.models.resource import Resource, ResourceAssignment
from backend.app.models.shelter import Shelter
from backend.app.models.road import RoadSegment, RoadCondition, Route
from backend.app.models.response_plan import ResponsePlan
from backend.app.services.world_engine import world_engine
from backend.app.services.routing_engine import RoutingEngine
from backend.app.agents.situation_agent import SituationAgent
from backend.app.agents.triage_agent import TriageAgent
from backend.app.agents.resource_agent import ResourceAllocationAgent
from backend.app.agents.shelter_agent import ShelterCapacityAgent
from backend.app.agents.verification_agent import VerificationAgent
from backend.app.agents.orchestrator import orchestrator
from backend.app.core.security import verify_password, hash_password, create_access_token, decode_access_token
from backend.app.scenarios.suryanagar_data import ROAD_NETWORK, SHELTERS, INITIAL_RESOURCES

def test_auth_and_passwords():
    pw = "Commander@123"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed)
    assert not verify_password("WrongPassword", hashed)
    
    token = create_access_token("user-123", "INCIDENT_COMMANDER", True)
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "INCIDENT_COMMANDER"
    assert payload["can_approve_dispatch"] is True

def test_duplicate_report_detection_and_situation_extraction():
    agent = SituationAgent()
    reports = [
        "Urgent flood emergency at Sector 1 Krishna Nagar: 25 people trapped on terrace with water 1.5m high!",
        "Second call Krishna Nagar Sector 1: 25 residents stranded on roof, 3 injured seniors need hospital."
    ]
    extracted = agent.deterministic_extract(reports, default_type="flood", sector="SEC-1")
    assert extracted["is_duplicate"] is True
    assert extracted["trapped_count"] >= 20
    assert extracted["medical_critical_count"] >= 2
    assert "Krishna" in extracted["summary"] or "trapped" in extracted["summary"]

def test_priority_calculations():
    triage = TriageAgent()
    crit_in = {"trapped_count": 28, "medical_critical_count": 6, "affected_count": 45, "disaster_type": "flood"}
    res = triage.deterministic_triage(crit_in)
    assert res["severity"] == "CRITICAL"
    assert res["priority_score"] >= 85.0
    assert "RESCUE_BOAT" in res["recommended_capabilities"]
    assert res["urgency_window_minutes"] <= 45

def test_resource_allocation_and_double_booking_prevention():
    res_agent = ResourceAllocationAgent()
    mock_resources = [
        {"id": "r-1", "name": "Boat 1", "callsign": "BOAT-01", "resource_type": "RESCUE_BOAT", "status": "AVAILABLE", "is_operational": True, "current_latitude": 16.51, "current_longitude": 80.64, "speed_kmh": 30.0},
        {"id": "r-2", "name": "Ambulance 1", "callsign": "AMB-01", "resource_type": "AMBULANCE", "status": "AVAILABLE", "is_operational": True, "current_latitude": 16.50, "current_longitude": 80.63, "speed_kmh": 60.0},
        {"id": "r-3", "name": "Ambulance 2", "callsign": "AMB-02", "resource_type": "AMBULANCE", "status": "ASSIGNED", "is_operational": True, "current_latitude": 16.50, "current_longitude": 80.64, "speed_kmh": 60.0},
    ]
    
    # r-3 is already assigned
    allocated = res_agent.deterministic_allocate(
        incident_lat=16.5125,
        incident_lng=80.6418,
        recommended_caps=["RESCUE_BOAT", "AMBULANCE"],
        available_resources=mock_resources,
        currently_assigned_ids=["r-3"]
    )
    assigned_ids = [r["resource_id"] for r in allocated["allocated_resources"]]
    assert "r-1" in assigned_ids
    assert "r-2" in assigned_ids
    assert "r-3" not in assigned_ids # Strictly avoided double booking!

def test_route_calculation_and_closure_invalidation():
    # Build routing graph
    seg_dicts = []
    for s in ROAD_NETWORK:
        seg_dicts.append({
            "code": s["code"],
            "name": s["name"],
            "road_type": s["road_type"],
            "start_node": s["start_node"],
            "end_node": s["end_node"],
            "start_lat": s["start_lat"],
            "start_lng": s["start_lng"],
            "end_lat": s["end_lat"],
            "end_lng": s["end_lng"],
            "length_km": s["length_km"],
            "speed_limit_kmh": s["speed_limit_kmh"],
            "is_blocked": False
        })
    engine = RoutingEngine(seg_dicts)
    
    # Route from SEC-1 (Riverbank) to SEC-6 (Hospital)
    route = engine.calculate_route(16.5120, 80.6420, 16.5020, 80.6350)
    assert route["path_found"] is True
    assert route["total_distance_km"] > 0
    assert len(route["waypoints"]) >= 2
    
    # Check invalidation if RS-09 Causeway is blocked
    is_compromised, reason = engine.check_route_invalidation(route["segments"], ["RS-09"])
    if "RS-09" in route["segments"]:
        assert is_compromised is True
        assert "RS-09" in reason

def test_shelter_capacity_and_intake():
    sh_agent = ShelterCapacityAgent()
    mock_shelters = [
        {"id": "sh-1", "name": "Stadium Shelter", "latitude": 16.48, "longitude": 80.65, "total_capacity": 1000, "current_occupancy": 200, "status": "OPEN", "has_medical_facility": True},
        {"id": "sh-2", "name": "Small School", "latitude": 16.53, "longitude": 80.62, "total_capacity": 50, "current_occupancy": 45, "status": "OPEN", "has_medical_facility": False},
    ]
    res = sh_agent.deterministic_select(
        incident_lat=16.51, incident_lng=80.64,
        headcount_to_evacuate=30, requires_medical=True,
        shelters=mock_shelters
    )
    assert res["target_shelter_id"] == "sh-1"
    assert res["remaining_capacity_after"] == (1000 - 200 - 30)
    assert res["has_medical_support"] is True

def test_verification_agent_rigor():
    verifier = VerificationAgent()
    
    valid_plan = {
        "resources": [{"resource_id": "r-1", "callsign": "AMB-01"}],
        "route": {"segments": ["RS-03", "RS-06"]},
        "shelter": {"target_shelter_id": "sh-1", "allocated_headcount": 10}
    }
    live_res = [{"id": "r-1", "callsign": "AMB-01", "status": "AVAILABLE"}]
    blocked = ["RS-01"] # Non-overlapping
    live_sh = [{"id": "sh-1", "name": "Shelter 1", "total_capacity": 100, "current_occupancy": 20}]
    
    passed = verifier.deterministic_verify(valid_plan, live_res, blocked, live_sh)
    assert passed["is_verified"] is True
    assert passed["verification_score"] >= 90

    # Invalidate when route crosses blocked segment
    invalid_plan = {
        "resources": [{"resource_id": "r-1", "callsign": "AMB-01"}],
        "route": {"segments": ["RS-01", "RS-03"]}, # RS-01 is blocked!
        "shelter": {"target_shelter_id": "sh-1", "allocated_headcount": 10}
    }
    failed = verifier.deterministic_verify(invalid_plan, live_res, blocked, live_sh)
    assert failed["is_verified"] is False
    assert any("CRITICAL ROUTE VIOLATION" in w for w in failed["warnings"])

def test_end_to_end_pipeline_and_replanning():
    async def run_scenario():
        await init_db()
        async with AsyncSessionLocal() as session:
            await world_engine.seed_initial_world(session)
            scenario = await world_engine.load_scenario(session, "flood")
            assert scenario.disaster_type == "flood"
            
            from sqlalchemy import select
            stmt = await session.execute(select(Incident).where(Incident.scenario_id == scenario.id))
            incident = stmt.scalars().first()
            assert incident is not None
            
            # Run 7-Agent pipeline
            pipeline_res = await orchestrator.run_full_pipeline(session, incident_id=incident.id)
            assert pipeline_res["is_verified"] is True
            assert pipeline_res["status"] == "AWAITING_APPROVAL"
            
            # Query active route to find the primary transit segment
            from backend.app.models.road import Route
            r_stmt = await session.execute(select(Route).where(Route.status == "ACTIVE"))
            active_route = r_stmt.scalars().first()
            assert active_route is not None
            traversed = json.loads(active_route.segments_traversed_json or "[]")
            target_segment = traversed[0] if traversed else "RS-09"

            # Continuous replanning trigger on traversed segment
            hazard_result = await world_engine.inject_hazard(
                session,
                segment_code=target_segment,
                blockage_type="FLOODED",
                description=f"Embankment breached. {target_segment} submerged under 75cm water."
            )
            assert hazard_result["status"] == "BLOCKED"
            assert len(hazard_result["replanned_plans"]) >= 1
            new_plan = hazard_result["replanned_plans"][0]
            assert "Rerouted" in new_plan["new_title"]
            assert new_plan["status"] == "AWAITING_APPROVAL"

    asyncio.run(run_scenario())
