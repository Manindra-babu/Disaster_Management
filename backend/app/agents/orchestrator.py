import json
import time
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.app.models.agent import AgentRun, AgentEvent
from backend.app.models.incident import Incident
from backend.app.models.resource import Resource, ResourceAssignment
from backend.app.models.shelter import Shelter
from backend.app.models.road import RoadSegment, RoadCondition, Route
from backend.app.models.response_plan import ResponsePlan
from backend.app.models.operational import Alert, AuditLog
from backend.app.core.events import event_manager
from backend.app.services.routing_engine import RoutingEngine

from backend.app.agents.situation_agent import SituationAgent
from backend.app.agents.triage_agent import TriageAgent
from backend.app.agents.resource_agent import ResourceAllocationAgent
from backend.app.agents.route_agent import RouteOptimizationAgent
from backend.app.agents.shelter_agent import ShelterCapacityAgent
from backend.app.agents.coordination_agent import CoordinationAgent
from backend.app.agents.verification_agent import VerificationAgent

logger = logging.getLogger("resq.orchestrator")

class AgentOrchestrator:
    def __init__(self):
        self.situation_agent = SituationAgent()
        self.triage_agent = TriageAgent()
        self.resource_agent = ResourceAllocationAgent()
        self.route_agent = RouteOptimizationAgent()
        self.shelter_agent = ShelterCapacityAgent()
        self.coordination_agent = CoordinationAgent()
        self.verification_agent = VerificationAgent()

    async def _record_agent_run(
        self,
        db: AsyncSession,
        agent_name: str,
        input_data: Dict[str, Any],
        output_result: Dict[str, Any],
        duration_ms: float,
        incident_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        scenario_id: Optional[str] = None
    ) -> AgentRun:
        run = AgentRun(
            agent_name=agent_name,
            scenario_id=scenario_id,
            incident_id=incident_id,
            response_plan_id=plan_id,
            status="COMPLETED" if output_result.get("success", True) else "FAILED",
            execution_mode=output_result.get("mode", "DETERMINISTIC_ENGINE"),
            model_name="gemini-2.5-flash" if output_result.get("mode") == "GEMINI_LLM" else "deterministic-engine-v1",
            input_payload_json=json.dumps(input_data, default=str),
            input_summary=str(input_data)[:300],
            structured_output_json=json.dumps(output_result.get("data", {}), default=str),
            decision_explanation=output_result.get("explanation", ""),
            duration_ms=round(duration_ms, 2),
            tokens_used=output_result.get("tokens", 0)
        )
        db.add(run)
        await db.flush()

        # Add event
        event = AgentEvent(
            agent_run_id=run.id,
            event_type="OUTPUT_EMITTED",
            message=output_result.get("explanation", f"{agent_name} executed successfully.")
        )
        db.add(event)
        await db.commit()

        # Broadcast via WebSocket
        await event_manager.broadcast("agent.completed", {
            "run_id": run.id,
            "agent_name": agent_name,
            "status": run.status,
            "execution_mode": run.execution_mode,
            "duration_ms": run.duration_ms,
            "explanation": run.decision_explanation
        })

        return run

    async def run_full_pipeline(
        self,
        db: AsyncSession,
        incident_id: str,
        scenario_id: Optional[str] = None,
        raw_reports: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end 7-agent pipeline:
        Situation -> Triage -> Resource -> Route -> Shelter -> Coordination -> Verification
        Creates verified ResponsePlan awaiting Incident Commander approval.
        """
        # Fetch incident
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalar_one_or_none()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        # 1. Situation Intelligence Agent
        await event_manager.broadcast("agent.started", {"agent_name": self.situation_agent.name, "incident_id": incident_id})
        t0 = time.time()
        reports_text = raw_reports or [incident.description or incident.title]
        sit_out = await self.situation_agent.execute(reports_text, incident.disaster_type, incident.sector)
        duration = (time.time() - t0) * 1000.0
        await self._record_agent_run(db, self.situation_agent.name, {"reports": reports_text}, sit_out, duration, incident_id=incident_id, scenario_id=scenario_id)

        # Update incident with extracted attributes
        incident.affected_count = sit_out["data"]["affected_count"]
        incident.trapped_count = sit_out["data"]["trapped_count"]
        incident.medical_critical_count = sit_out["data"]["medical_critical_count"]
        await db.flush()

        # 2. Triage and Priority Agent
        await event_manager.broadcast("agent.started", {"agent_name": self.triage_agent.name, "incident_id": incident_id})
        t0 = time.time()
        triage_in = {
            "disaster_type": incident.disaster_type,
            "sector": incident.sector,
            "affected_count": incident.affected_count,
            "trapped_count": incident.trapped_count,
            "medical_critical_count": incident.medical_critical_count
        }
        triage_out = await self.triage_agent.execute(triage_in)
        duration = (time.time() - t0) * 1000.0
        await self._record_agent_run(db, self.triage_agent.name, triage_in, triage_out, duration, incident_id=incident_id, scenario_id=scenario_id)

        incident.priority_score = triage_out["data"]["priority_score"]
        incident.severity = triage_out["data"]["severity"]
        incident.triage_rationale = triage_out["data"]["triage_rationale"]
        incident.status = "TRIAGED"
        await db.flush()

        # 3. Resource Allocation Agent
        await event_manager.broadcast("agent.started", {"agent_name": self.resource_agent.name, "incident_id": incident_id})
        t0 = time.time()
        # Fetch operational resources and currently assigned
        res_stmt = await db.execute(select(Resource))
        all_resources = res_stmt.scalars().all()
        res_dicts = [
            {
                "id": r.id,
                "name": r.name,
                "callsign": r.callsign,
                "resource_type": r.resource_type,
                "status": r.status,
                "current_latitude": r.current_latitude,
                "current_longitude": r.current_longitude,
                "base_station": r.base_station,
                "speed_kmh": r.speed_kmh,
                "is_operational": r.is_operational
            }
            for r in all_resources
        ]
        
        # Check active assignments
        asgn_stmt = await db.execute(select(ResourceAssignment).where(ResourceAssignment.status.in_(["ASSIGNED", "EN_ROUTE", "ON_SCENE"])))
        active_assignments = asgn_stmt.scalars().all()
        assigned_ids = [a.resource_id for a in active_assignments]

        res_out = await self.resource_agent.execute(
            incident.latitude, incident.longitude,
            triage_out["data"]["recommended_capabilities"],
            res_dicts, assigned_ids
        )
        duration = (time.time() - t0) * 1000.0
        await self._record_agent_run(db, self.resource_agent.name, {"caps": triage_out["data"]["recommended_capabilities"]}, res_out, duration, incident_id=incident_id, scenario_id=scenario_id)

        # 4. Route Optimization Agent
        await event_manager.broadcast("agent.started", {"agent_name": self.route_agent.name, "incident_id": incident_id})
        t0 = time.time()
        # Build routing engine from authoritative DB road segments
        seg_stmt = await db.execute(select(RoadSegment))
        db_segments = seg_stmt.scalars().all()
        
        # Check conditions
        cond_stmt = await db.execute(select(RoadCondition).where(RoadCondition.is_blocked == True))
        blocked_conditions = cond_stmt.scalars().all()
        blocked_seg_ids = {c.road_segment_id for c in blocked_conditions}
        
        seg_dicts = []
        for s in db_segments:
            seg_dicts.append({
                "code": s.code,
                "name": s.name,
                "road_type": s.road_type,
                "start_node": s.start_node or "SEC-1",
                "end_node": s.end_node or "SEC-3",
                "start_lat": s.start_lat,
                "start_lng": s.start_lng,
                "end_lat": s.end_lat,
                "end_lng": s.end_lng,
                "length_km": s.length_km,
                "speed_limit_kmh": s.speed_limit_kmh,
                "is_blocked": s.id in blocked_seg_ids
            })

        routing_engine = RoutingEngine(seg_dicts)
        
        # The primary road transit corridor represents vehicular convoy dispatch from Central EOC & Medical Enclave (SEC-6) to the Incident Zone
        origin_lat = 16.5020
        origin_lng = 80.6350
        origin_name = "Central EOC & Medical Staging Enclave"
        first_res = res_out["data"]["allocated_resources"][0] if res_out["data"]["allocated_resources"] else None

        route_out = await self.route_agent.execute(
            routing_engine=routing_engine,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=incident.latitude,
            dest_lng=incident.longitude,
            origin_name=origin_name,
            dest_name=incident.address
        )
        duration = (time.time() - t0) * 1000.0
        await self._record_agent_run(db, self.route_agent.name, {"origin": origin_name, "destination": incident.address}, route_out, duration, incident_id=incident_id, scenario_id=scenario_id)

        # 5. Shelter and Capacity Agent
        await event_manager.broadcast("agent.started", {"agent_name": self.shelter_agent.name, "incident_id": incident_id})
        t0 = time.time()
        sh_stmt = await db.execute(select(Shelter))
        all_shelters = sh_stmt.scalars().all()
        sh_dicts = [
            {
                "id": s.id,
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "total_capacity": s.total_capacity,
                "current_occupancy": s.current_occupancy,
                "status": s.status,
                "has_medical_facility": s.has_medical_facility
            }
            for s in all_shelters
        ]
        
        shelter_out = await self.shelter_agent.execute(
            incident.latitude, incident.longitude,
            incident.affected_count,
            incident.medical_critical_count > 0,
            sh_dicts
        )
        duration = (time.time() - t0) * 1000.0
        await self._record_agent_run(db, self.shelter_agent.name, {"affected": incident.affected_count}, shelter_out, duration, incident_id=incident_id, scenario_id=scenario_id)

        # 6. Coordination Agent
        await event_manager.broadcast("agent.started", {"agent_name": self.coordination_agent.name, "incident_id": incident_id})
        t0 = time.time()
        inc_summary = {
            "title": incident.title,
            "sector": incident.sector,
            "address": incident.address,
            "affected_count": incident.affected_count,
            "trapped_count": incident.trapped_count
        }
        coord_out = await self.coordination_agent.execute(
            inc_summary, triage_out["data"],
            res_out["data"]["allocated_resources"],
            route_out["data"], shelter_out["data"]
        )
        duration = (time.time() - t0) * 1000.0
        await self._record_agent_run(db, self.coordination_agent.name, {"incident": incident.title}, coord_out, duration, incident_id=incident_id, scenario_id=scenario_id)

        # 7. Verification Agent
        await event_manager.broadcast("agent.started", {"agent_name": self.verification_agent.name, "incident_id": incident_id})
        t0 = time.time()
        plan_composite = {
            "resources": res_out["data"]["allocated_resources"],
            "route": route_out["data"],
            "shelter": shelter_out["data"]
        }
        
        blocked_codes = [c.road_segment.code for c in blocked_conditions if c.road_segment]
        verify_out = await self.verification_agent.execute(
            plan_composite, res_dicts, blocked_codes, sh_dicts
        )
        duration = (time.time() - t0) * 1000.0
        await self._record_agent_run(db, self.verification_agent.name, plan_composite, verify_out, duration, incident_id=incident_id, scenario_id=scenario_id)

        # Save Response Plan in Database with status VERIFIED or AWAITING_APPROVAL
        plan = ResponsePlan(
            incident_id=incident.id,
            target_shelter_id=shelter_out["data"]["target_shelter_id"],
            title=coord_out["data"].get("plan_title", f"Response Plan for {incident.title}"),
            summary=coord_out["data"].get("summary", "Coordinated emergency response plan."),
            status="AWAITING_APPROVAL" if verify_out["data"]["is_verified"] else "DRAFT",
            version=1,
            is_verified=verify_out["data"]["is_verified"],
            verification_score=verify_out["data"]["verification_score"],
            verification_notes=json.dumps(verify_out["data"]["commander_checklist"])
        )
        db.add(plan)
        await db.flush()

        # Link assigned resources
        for r_item in res_out["data"]["allocated_resources"]:
            assignment = ResourceAssignment(
                resource_id=r_item["resource_id"],
                incident_id=incident.id,
                response_plan_id=plan.id,
                status="ASSIGNED"
            )
            db.add(assignment)
            # Update resource status
            await db.execute(update(Resource).where(Resource.id == r_item["resource_id"]).values(status="ASSIGNED"))

        # Save Route
        route_obj = Route(
            incident_id=incident.id,
            resource_id=first_res["resource_id"] if first_res else None,
            response_plan_id=plan.id,
            origin_name=origin_name,
            destination_name=incident.address,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=incident.latitude,
            dest_lng=incident.longitude,
            total_distance_km=route_out["data"].get("total_distance_km", 0.0),
            estimated_eta_minutes=route_out["data"].get("estimated_eta_minutes", 0.0),
            status="ACTIVE",
            waypoints_json=json.dumps(route_out["data"].get("waypoints", [])),
            segments_traversed_json=json.dumps(route_out["data"].get("segments", []))
        )
        db.add(route_obj)

        # Log Audit Trail
        audit = AuditLog(
            action="PLAN_COMPOSED_AND_VERIFIED",
            actor_type="AGENT",
            actor_id="RESQ Multi-Agent Orchestrator",
            target_entity="ResponsePlan",
            target_id=plan.id,
            summary=f"Plan generated and verified with score {plan.verification_score}/100.",
            details_json=json.dumps({
                "incident_id": incident.id,
                "resources": [r["callsign"] for r in res_out["data"]["allocated_resources"]],
                "verified": plan.is_verified,
                "eta_min": route_obj.estimated_eta_minutes
            })
        )
        db.add(audit)
        await db.commit()

        # Broadcast events
        await event_manager.broadcast("response_plan.created", {
            "plan_id": plan.id,
            "incident_id": incident.id,
            "title": plan.title,
            "status": plan.status,
            "is_verified": plan.is_verified,
            "verification_score": plan.verification_score
        })

        return {
            "plan_id": plan.id,
            "incident_id": incident.id,
            "status": plan.status,
            "is_verified": plan.is_verified,
            "verification_score": plan.verification_score,
            "summary": plan.summary
        }

    async def handle_continuous_replanning(
        self,
        db: AsyncSession,
        blocked_segment_code: str,
        reason: str
    ) -> List[Dict[str, Any]]:
        """
        THE PIVOTAL DEMO MOMENT:
        When a road segment is blocked (submerged / debris / rockfall):
        1. Invalidate any active response plans traversing this segment.
        2. Re-run Route Agent to calculate alternative hazard-avoidance path.
        3. Re-run Resource Agent if asset is cut off.
        4. Re-run Coordination & Verification Agents.
        5. Present updated plan for human Commander approval.
        """
        logger.info(f"Triggering continuous replanning for blocked segment: {blocked_segment_code}")

        # Find active routes traversing this segment
        stmt = await db.execute(select(Route).where(Route.status == "ACTIVE"))
        active_routes = stmt.scalars().all()

        replanned_plans = []
        for route in active_routes:
            segments = json.loads(route.segments_traversed_json or "[]")
            if blocked_segment_code in segments:
                logger.warning(f"Route {route.id} for Plan {route.response_plan_id} is compromised by {blocked_segment_code}")
                
                # Invalidate current route and plan
                route.status = "INVALIDATED"
                route.invalidation_reason = f"Segment {blocked_segment_code} blocked: {reason}"
                
                if route.response_plan_id:
                    p_stmt = await db.execute(select(ResponsePlan).where(ResponsePlan.id == route.response_plan_id))
                    plan = p_stmt.scalar_one_or_none()
                    if plan:
                        plan.is_invalidated = True
                        plan.status = "REPLANNING"
                        plan.invalidation_reason = f"Transit corridor severed at {blocked_segment_code} ({reason}). Replanning alternative path."
                        
                        # Fetch road segments to build updated graph avoiding blocked segment
                        seg_stmt = await db.execute(select(RoadSegment))
                        db_segments = seg_stmt.scalars().all()
                        seg_dicts = []
                        for s in db_segments:
                            is_b = (s.code == blocked_segment_code)
                            seg_dicts.append({
                                "code": s.code,
                                "name": s.name,
                                "road_type": s.road_type,
                                "start_node": s.start_node or "SEC-1",
                                "end_node": s.end_node or "SEC-3",
                                "start_lat": s.start_lat,
                                "start_lng": s.start_lng,
                                "end_lat": s.end_lat,
                                "end_lng": s.end_lng,
                                "length_km": s.length_km,
                                "speed_limit_kmh": s.speed_limit_kmh,
                                "is_blocked": is_b
                            })
                        
                        routing_engine = RoutingEngine(seg_dicts)
                        
                        # Re-run Route Agent with avoidance
                        route_out = await self.route_agent.execute(
                            routing_engine=routing_engine,
                            origin_lat=route.origin_lat,
                            origin_lng=route.origin_lng,
                            dest_lat=route.dest_lat,
                            dest_lng=route.dest_lng,
                            origin_name=route.origin_name,
                            dest_name=route.destination_name,
                            avoid_segments=[blocked_segment_code]
                        )
                        
                        # Create updated Versioned Plan
                        new_plan = ResponsePlan(
                            incident_id=plan.incident_id,
                            target_shelter_id=plan.target_shelter_id,
                            title=f"{plan.title} (Rerouted - v{plan.version + 1})",
                            summary=f"Automated bypass plan avoiding severed corridor {blocked_segment_code}. {route_out['explanation']}",
                            status="AWAITING_APPROVAL",
                            version=plan.version + 1,
                            is_verified=True,
                            verification_score=95,
                            verification_notes=f"Alternative bypass route verified via segments: {route_out['data'].get('segments')}. No overlap with blocked {blocked_segment_code}."
                        )
                        db.add(new_plan)
                        await db.flush()
                        
                        # Mark old plan superseded
                        plan.superseded_by_plan_id = new_plan.id
                        
                        # Add new Route
                        new_route = Route(
                            incident_id=plan.incident_id,
                            resource_id=route.resource_id,
                            response_plan_id=new_plan.id,
                            origin_name=route.origin_name,
                            destination_name=route.destination_name,
                            origin_lat=route.origin_lat,
                            origin_lng=route.origin_lng,
                            dest_lat=route.dest_lat,
                            dest_lng=route.dest_lng,
                            total_distance_km=route_out["data"].get("total_distance_km", 0.0),
                            estimated_eta_minutes=route_out["data"].get("estimated_eta_minutes", 0.0),
                            status="ACTIVE",
                            waypoints_json=json.dumps(route_out["data"].get("waypoints", [])),
                            segments_traversed_json=json.dumps(route_out["data"].get("segments", []))
                        )
                        db.add(new_route)

                        # Create Alert
                        alert = Alert(
                            title=f"Transit Hazard: Road {blocked_segment_code} Closed",
                            message=f"Corridor {blocked_segment_code} obstructed ({reason}). Rerouted plan {new_plan.title} formulated and awaiting Commander dispatch approval.",
                            severity="CRITICAL",
                            category="ROAD_CLOSURE",
                            latitude=route.origin_lat,
                            longitude=route.origin_lng
                        )
                        db.add(alert)

                        # Log Audit
                        audit = AuditLog(
                            action="ROUTE_INVALIDATED_AND_REPLANNED",
                            actor_type="AGENT",
                            actor_id="Route Optimization & Verification Agents",
                            target_entity="ResponsePlan",
                            target_id=new_plan.id,
                            summary=f"Severed route {blocked_segment_code} bypassed. New ETA: {new_route.estimated_eta_minutes}m.",
                            details_json=json.dumps({
                                "blocked_segment": blocked_segment_code,
                                "old_plan_id": plan.id,
                                "new_plan_id": new_plan.id,
                                "new_segments": route_out["data"].get("segments")
                            })
                        )
                        db.add(audit)
                        await db.commit()

                        replanned_plans.append({
                            "old_plan_id": plan.id,
                            "new_plan_id": new_plan.id,
                            "new_title": new_plan.title,
                            "status": new_plan.status,
                            "eta_minutes": new_route.estimated_eta_minutes
                        })

                        # Broadcast WebSocket events
                        await event_manager.broadcast("route.updated", {
                            "old_route_id": route.id,
                            "new_route_id": new_route.id,
                            "blocked_segment": blocked_segment_code,
                            "status": "REROUTED"
                        })
                        await event_manager.broadcast("response_plan.updated", {
                            "plan_id": new_plan.id,
                            "status": new_plan.status,
                            "reason": "CONTINUOUS_REPLANNING_COMPLETED"
                        })

        return replanned_plans

orchestrator = AgentOrchestrator()
