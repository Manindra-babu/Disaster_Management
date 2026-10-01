import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from backend.app.models.user import User, Role
from backend.app.models.incident import Incident, IncidentReport
from backend.app.models.resource import Resource, ResourceAssignment
from backend.app.models.shelter import Shelter, ShelterCapacity
from backend.app.models.road import RoadSegment, RoadCondition, Route
from backend.app.models.response_plan import ResponsePlan
from backend.app.models.agent import AgentRun, AgentEvent
from backend.app.models.simulation import SimulationScenario, SimulationEvent
from backend.app.models.operational import Alert, AuditLog
from backend.app.core.security import hash_password
from backend.app.core.events import event_manager
from backend.app.scenarios.suryanagar_data import (
    ROAD_NETWORK, SHELTERS, INITIAL_RESOURCES, DISASTER_SCENARIOS
)
from backend.app.agents.orchestrator import orchestrator

logger = logging.getLogger("resq.world_engine")

class WorldEngine:
    def __init__(self):
        self.active_scenario_type = "flood"

    async def seed_initial_world(self, db: AsyncSession) -> None:
        """Seeds roles, initial users, road segments, shelters, and resources."""
        # 1. Check if roles exist
        r_stmt = await db.execute(select(Role))
        existing_roles = r_stmt.scalars().all()
        if not existing_roles:
            roles = [
                Role(name="INCIDENT_COMMANDER", description="Can approve dispatch, override agent plans, manage state", can_approve_dispatch=True, can_manage_simulations=True, can_edit_resources=True),
                Role(name="OPERATOR", description="Can submit reports, manage resources, trigger simulation events", can_approve_dispatch=False, can_manage_simulations=True, can_edit_resources=True),
                Role(name="VIEWER", description="Read-only access to GIS map, KPIs, and agent observatory", can_approve_dispatch=False, can_manage_simulations=False, can_edit_resources=False),
                Role(name="ADMINISTRATOR", description="System administrator with full control", can_approve_dispatch=True, can_manage_simulations=True, can_edit_resources=True),
            ]
            db.add_all(roles)
            await db.flush()

            # Seed demo users
            cmd_role = next(r for r in roles if r.name == "INCIDENT_COMMANDER")
            op_role = next(r for r in roles if r.name == "OPERATOR")
            view_role = next(r for r in roles if r.name == "VIEWER")

            users = [
                User(email="commander@resq.gov.in", full_name="Commander Rajesh Patel", hashed_password=hash_password("Commander@123"), role_id=cmd_role.id),
                User(email="operator@resq.gov.in", full_name="Duty Officer Priya Nair", hashed_password=hash_password("Operator@123"), role_id=op_role.id),
                User(email="viewer@resq.gov.in", full_name="GIS Analyst Amit Sen", hashed_password=hash_password("Viewer@123"), role_id=view_role.id),
            ]
            db.add_all(users)
            await db.flush()

        # 2. Seed Road Segments if empty
        seg_stmt = await db.execute(select(RoadSegment))
        if not seg_stmt.scalars().first():
            road_objs = []
            for r in ROAD_NETWORK:
                road_objs.append(RoadSegment(
                    code=r["code"],
                    name=r["name"],
                    road_type=r["road_type"],
                    start_node=r.get("start_node", "SEC-1"),
                    end_node=r.get("end_node", "SEC-3"),
                    start_lat=r["start_lat"],
                    start_lng=r["start_lng"],
                    end_lat=r["end_lat"],
                    end_lng=r["end_lng"],
                    length_km=r["length_km"],
                    speed_limit_kmh=r["speed_limit_kmh"]
                ))
            db.add_all(road_objs)
            await db.flush()

        # 3. Seed Shelters if empty
        sh_stmt = await db.execute(select(Shelter))
        if not sh_stmt.scalars().first():
            shelter_objs = []
            for s in SHELTERS:
                shelter_objs.append(Shelter(
                    name=s["name"],
                    code=s["code"],
                    address=s["address"],
                    sector=s["sector"],
                    latitude=s["lat"],
                    longitude=s["lng"],
                    total_capacity=s["total_capacity"],
                    current_occupancy=s["current_occupancy"],
                    status=s["status"],
                    has_medical_facility=s["has_medical_facility"],
                    has_power_backup=s["has_power_backup"],
                    food_days_remaining=s["food_days"],
                    water_liters_available=s["water_liters"],
                    contact_person=s["contact_person"],
                    contact_phone=s["contact_phone"]
                ))
            db.add_all(shelter_objs)
            await db.flush()

        # 4. Seed Resources if empty
        res_stmt = await db.execute(select(Resource))
        if not res_stmt.scalars().first():
            resource_objs = []
            for res in INITIAL_RESOURCES:
                resource_objs.append(Resource(
                    name=res["name"],
                    callsign=res["callsign"],
                    resource_type=res["resource_type"],
                    capacity=res["capacity"],
                    base_station=res["base_station"],
                    current_latitude=res["lat"],
                    current_longitude=res["lng"],
                    speed_kmh=res["speed_kmh"],
                    status="AVAILABLE",
                    fuel_percent=100,
                    is_operational=True
                ))
            db.add_all(resource_objs)
            await db.flush()

        await db.commit()

    async def load_scenario(self, db: AsyncSession, disaster_type: str) -> SimulationScenario:
        """
        Loads a disaster scenario (flood, cyclone, earthquake, wildfire, landslide).
        Clears previous dynamic runs, resets road conditions and resources,
        and spawns the initial scenario events.
        """
        if disaster_type not in DISASTER_SCENARIOS:
            disaster_type = "flood"

        self.active_scenario_type = disaster_type
        sc_data = DISASTER_SCENARIOS[disaster_type]

        # Reset dynamic tables
        await db.execute(delete(ResourceAssignment))
        await db.execute(delete(Route))
        await db.execute(delete(ResponsePlan))
        await db.execute(delete(IncidentReport))
        await db.execute(delete(Incident))
        await db.execute(delete(RoadCondition))
        await db.execute(delete(AgentEvent))
        await db.execute(delete(AgentRun))
        await db.execute(delete(SimulationEvent))
        await db.execute(delete(SimulationScenario))
        await db.execute(delete(Alert))

        # Reset all resources to AVAILABLE
        await db.execute(update(Resource).values(status="AVAILABLE"))

        # Create scenario record
        scenario = SimulationScenario(
            name=sc_data["name"],
            disaster_type=disaster_type,
            location_name="Suryanagar, India",
            description=sc_data["description"],
            status="IDLE",
            current_tick=0,
            speed_multiplier=1.0,
            seed=42,
            weather_summary=sc_data["weather_summary"],
            wind_speed_kmh=sc_data["wind_speed_kmh"],
            rainfall_mm=sc_data["rainfall_mm"]
        )
        db.add(scenario)
        await db.flush()

        # Seed initial scenario incidents and reports
        for inc_item in sc_data["initial_incidents"]:
            inc = Incident(
                scenario_id=scenario.id,
                title=inc_item["title"],
                description=inc_item["description"],
                disaster_type=inc_item["disaster_type"],
                severity=inc_item["severity"],
                status="REPORTED",
                latitude=inc_item["lat"],
                longitude=inc_item["lng"],
                address=inc_item["address"],
                sector=inc_item["sector"],
                affected_count=inc_item["affected_count"],
                trapped_count=inc_item["trapped_count"],
                medical_critical_count=inc_item["medical_critical_count"],
                priority_score=inc_item["priority_score"],
                triage_rationale=inc_item["triage_rationale"],
                is_verified=False
            )
            db.add(inc)
            await db.flush()

            # Add reports
            for rep_text in inc_item.get("reports", []):
                rep = IncidentReport(
                    incident_id=inc.id,
                    source="EMERGENCY_CALL",
                    raw_text=rep_text,
                    latitude=inc.latitude,
                    longitude=inc.longitude,
                    location_name=inc.address,
                    is_processed=False
                )
                db.add(rep)

        # Seed scheduled simulation events
        for ev in sc_data.get("hazard_events", []):
            simev = SimulationEvent(
                scenario_id=scenario.id,
                tick=ev["tick"],
                event_type=ev["event_type"],
                title=ev["title"],
                description=ev["description"],
                payload_json=json.dumps(ev["payload"]),
                is_executed=False
            )
            db.add(simev)

        # Initial Alert
        alert = Alert(
            title=f"Simulation Initialized: {scenario.name}",
            message=f"Disaster profile loaded for Suryanagar ({disaster_type.upper()}). World state reset to baseline.",
            severity="WARNING",
            category="WEATHER"
        )
        db.add(alert)

        # Initial Audit Log
        audit = AuditLog(
            action="SIMULATION_SCENARIO_LOADED",
            actor_type="SYSTEM",
            actor_id="RESQ World Engine",
            target_entity="SimulationScenario",
            target_id=scenario.id,
            summary=f"Loaded {sc_data['name']} with {len(sc_data['initial_incidents'])} initial incidents.",
            details_json=json.dumps({"disaster_type": disaster_type, "seed": 42})
        )
        db.add(audit)

        await db.commit()

        # Broadcast WebSocket event
        await event_manager.broadcast("simulation.event", {
            "action": "SCENARIO_LOADED",
            "scenario_id": scenario.id,
            "disaster_type": disaster_type,
            "name": scenario.name
        })

        return scenario

    async def advance_tick(self, db: AsyncSession, scenario_id: str) -> Dict[str, Any]:
        """Advances simulation world by 1 tick, triggering scheduled events."""
        stmt = await db.execute(select(SimulationScenario).where(SimulationScenario.id == scenario_id))
        scenario = stmt.scalar_one_or_none()
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        scenario.current_tick += 1
        current_tick = scenario.current_tick

        # Check for unexecuted events at this tick
        ev_stmt = await db.execute(
            select(SimulationEvent).where(
                SimulationEvent.scenario_id == scenario.id,
                SimulationEvent.tick <= current_tick,
                SimulationEvent.is_executed == False
            )
        )
        events_to_run = ev_stmt.scalars().all()
        executed_events = []

        for ev in events_to_run:
            ev.is_executed = True
            payload = json.loads(ev.payload_json or "{}")

            if ev.event_type == "ROAD_BLOCKAGE":
                seg_code = payload.get("segment_code")
                # Block the road segment
                r_stmt = await db.execute(select(RoadSegment).where(RoadSegment.code == seg_code))
                road = r_stmt.scalar_one_or_none()
                if road:
                    cond = RoadCondition(
                        road_segment_id=road.id,
                        status=payload.get("status", "DEBRIS_BLOCKED"),
                        is_blocked=True,
                        hazard_severity=8,
                        water_depth_cm=payload.get("water_depth_cm", 0),
                        obstruction_details=payload.get("obstruction_details", ev.description),
                        passable_for_boat=payload.get("passable_for_boat", False),
                        passable_for_high_clearance=payload.get("passable_for_high_clearance", False)
                    )
                    db.add(cond)
                    await db.flush()

                    # Trigger Continuous Replanning!
                    await orchestrator.handle_continuous_replanning(
                        db, seg_code, ev.description
                    )

            executed_events.append({"id": ev.id, "title": ev.title, "type": ev.event_type})

        # Advance movement of dispatched resources
        res_stmt = await db.execute(select(Resource).where(Resource.status.in_(["IN_TRANSIT", "ASSIGNED"])))
        in_transit_resources = res_stmt.scalars().all()
        for r in in_transit_resources:
            # Gradually update status to ON_SCENE if in transit
            if r.status == "IN_TRANSIT":
                r.status = "ON_SCENE"
                await event_manager.broadcast("resource.updated", {"resource_id": r.id, "status": "ON_SCENE"})

        await db.commit()

        await event_manager.broadcast("simulation.event", {
            "action": "TICK_ADVANCED",
            "current_tick": current_tick,
            "executed_events": executed_events
        })

        return {
            "current_tick": current_tick,
            "status": scenario.status,
            "events_triggered": executed_events
        }

    async def inject_hazard(self, db: AsyncSession, segment_code: str, blockage_type: str, description: str) -> Dict[str, Any]:
        """Allows user or operator to manually inject a hazard to trigger replanning."""
        r_stmt = await db.execute(select(RoadSegment).where(RoadSegment.code == segment_code))
        road = r_stmt.scalar_one_or_none()
        if not road:
            raise ValueError(f"Road segment {segment_code} not found")

        cond = RoadCondition(
            road_segment_id=road.id,
            status=blockage_type,
            is_blocked=True,
            hazard_severity=9,
            obstruction_details=description
        )
        db.add(cond)
        await db.flush()

        # Trigger Continuous Replanning
        replanned = await orchestrator.handle_continuous_replanning(db, segment_code, description)
        await db.commit()

        return {
            "segment_code": segment_code,
            "status": "BLOCKED",
            "replanned_plans": replanned
        }

world_engine = WorldEngine()
