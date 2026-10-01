import logging
from typing import Dict, Any, List
from backend.app.agents.gemini_client import gemini_client

logger = logging.getLogger("resq.agent.coordination")

SYSTEM_INSTRUCTION = """
You are the Coordination Agent for RESQ.
Synthesize the intelligence, triage priority, assigned resources, transit routes, and shelter destination
into a cohesive, professional Incident Response Plan for the Incident Commander.
Return JSON:
{
  "plan_title": "string",
  "summary": "string",
  "operational_objectives": ["string"],
  "execution_phases": [
    {
      "phase_number": integer,
      "title": "string",
      "action": "string"
    }
  ],
  "contingency_measures": "string"
}
"""

class CoordinationAgent:
    def __init__(self):
        self.name = "Coordination Agent"

    def deterministic_coordinate(
        self,
        incident: Dict[str, Any],
        triage: Dict[str, Any],
        resources: List[Dict[str, Any]],
        route: Dict[str, Any],
        shelter: Dict[str, Any]
    ) -> Dict[str, Any]:
        title = f"Operations Action Plan: {incident.get('title', 'Emergency Response')}"
        summary = (
            f"Coordinated multi-agency response targeting {incident.get('affected_count', 0)} citizens in {incident.get('sector', 'SEC-1')}. "
            f"Severity evaluated as {triage.get('severity', 'HIGH')} (Score {triage.get('priority_score', 0)}). "
            f"Deploying {len(resources)} operational assets ({', '.join(r.get('callsign', '') for r in resources)}). "
            f"Primary transit distance {route.get('total_distance_km', 0)} km, estimated arrival in {route.get('estimated_eta_minutes', 0)} mins. "
            f"Civilian casualties and evacuees routed to {shelter.get('shelter_name', 'Designated Shelter')}."
        )

        phases = [
            {
                "phase_number": 1,
                "title": "Immediate Deployment & Route Ingress",
                "action": f"Dispatch units {', '.join(r.get('callsign', '') for r in resources)} via clear corridors to {incident.get('address', 'scene')}."
            },
            {
                "phase_number": 2,
                "title": "Search, Extrication & Medical Stabilization",
                "action": f"Establish on-scene triage perimeter, extricate {incident.get('trapped_count', 0)} trapped citizens, provide high-acuity trauma care."
            },
            {
                "phase_number": 3,
                "title": "Evacuation & Humanitarian Shelter Intake",
                "action": f"Relocate evacuees to {shelter.get('shelter_name', 'Shelter')} with continuous headroom monitoring."
            }
        ]

        objectives = [
            f"Zero loss of life among {incident.get('trapped_count', 0)} trapped citizens.",
            f"Maintain secure ingress along {route.get('total_distance_km', 0)}km transit corridor.",
            f"Expedite transfer of critical casualties to equipped trauma facilities."
        ]

        return {
            "plan_title": title,
            "summary": summary,
            "operational_objectives": objectives,
            "execution_phases": phases,
            "contingency_measures": "If primary transit corridor suffers secondary hazard obstruction, automated replanning sub-routine will calculate alternate bypass."
        }

    async def execute(
        self,
        incident: Dict[str, Any],
        triage: Dict[str, Any],
        resources: List[Dict[str, Any]],
        route: Dict[str, Any],
        shelter: Dict[str, Any]
    ) -> Dict[str, Any]:
        fallback_data = self.deterministic_coordinate(incident, triage, resources, route, shelter)

        prompt = f"""
Synthesize Incident Response Plan:
Incident: {incident.get('title')} ({incident.get('sector')})
Triage: {triage.get('severity')} - Score {triage.get('priority_score')}
Assigned Units: {[r.get('callsign') for r in resources]}
Route: {route.get('total_distance_km')} km, ETA {route.get('estimated_eta_minutes')} min
Target Shelter: {shelter.get('shelter_name')}

Generate professional operational briefing and phased directives for the Incident Commander.
"""
        success, parsed, mode, tokens = await gemini_client.generate_structured(
            system_instruction=SYSTEM_INSTRUCTION,
            prompt=prompt
        )

        if success and parsed.get("summary"):
            return {
                "success": True,
                "data": parsed,
                "mode": mode,
                "tokens": tokens,
                "explanation": parsed.get("summary")
            }

        return {
            "success": True,
            "data": fallback_data,
            "mode": "DETERMINISTIC_ENGINE",
            "tokens": 0,
            "explanation": fallback_data["summary"]
        }
