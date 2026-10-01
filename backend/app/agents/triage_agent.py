import logging
from typing import Dict, Any, List
from backend.app.agents.gemini_client import gemini_client

logger = logging.getLogger("resq.agent.triage")

SYSTEM_INSTRUCTION = """
You are the Triage and Priority Agent for RESQ emergency operations.
Analyze incident metrics (trapped persons, critical medical cases, environmental hazards)
and explain a deterministic priority calculation.
Return strictly JSON with:
{
  "priority_score": float (0.0 to 100.0),
  "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "urgency_window_minutes": integer,
  "triage_rationale": "string",
  "recommended_capabilities": ["string"]
}
"""

class TriageAgent:
    def __init__(self):
        self.name = "Triage and Priority Agent"

    def deterministic_triage(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        trapped = incident_data.get("trapped_count", 0)
        med_crit = incident_data.get("medical_critical_count", 0)
        affected = incident_data.get("affected_count", 0)
        dtype = incident_data.get("disaster_type", "flood").lower()
        
        # Base formula: trapped*2.5 + med_crit*4.0 + affected*0.5
        score = 40.0 + (trapped * 2.2) + (med_crit * 3.8) + (min(affected, 50) * 0.4)
        score = min(99.0, max(25.0, score))
        
        if score >= 85.0 or med_crit >= 4 or trapped >= 15:
            severity = "CRITICAL"
            urgency_min = 30
        elif score >= 70.0:
            severity = "HIGH"
            urgency_min = 60
        elif score >= 50.0:
            severity = "MEDIUM"
            urgency_min = 120
        else:
            severity = "LOW"
            urgency_min = 240

        caps = []
        if dtype == "flood":
            caps.extend(["RESCUE_BOAT", "AMBULANCE", "EVACUATION_BUS"])
        elif dtype == "cyclone":
            caps.extend(["EVACUATION_BUS", "AMBULANCE", "GENERATOR", "WATER_TANKER"])
        elif dtype == "earthquake":
            caps.extend(["RESCUE_TEAM", "AMBULANCE", "MOBILE_MEDICAL_UNIT"])
        elif dtype == "wildfire":
            caps.extend(["FIRE_UNIT", "WATER_TANKER", "EVACUATION_BUS"])
        elif dtype == "landslide":
            caps.extend(["RESCUE_TEAM", "AMBULANCE", "RELIEF_TRUCK"])

        rationale = (
            f"Triage calculation: Score {round(score, 1)} ({severity}). "
            f"Immediate life hazard for {trapped} trapped individuals and {med_crit} high-acuity medical cases. "
            f"Operational intervention window established at {urgency_min} minutes."
        )

        return {
            "priority_score": round(score, 1),
            "severity": severity,
            "urgency_window_minutes": urgency_min,
            "triage_rationale": rationale,
            "recommended_capabilities": caps
        }

    async def execute(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
Incident Data:
Trapped Count: {incident_data.get('trapped_count', 0)}
Medical Critical: {incident_data.get('medical_critical_count', 0)}
Total Affected: {incident_data.get('affected_count', 0)}
Disaster Type: {incident_data.get('disaster_type', 'unknown')}
Sector: {incident_data.get('sector', 'SEC-1')}

Calculate priority, severity, urgency window, and justify the clinical and operational response urgency.
"""
        success, parsed, mode, tokens = await gemini_client.generate_structured(
            system_instruction=SYSTEM_INSTRUCTION,
            prompt=prompt
        )

        if success and "priority_score" in parsed and "severity" in parsed:
            return {
                "success": True,
                "data": parsed,
                "mode": mode,
                "tokens": tokens,
                "explanation": parsed.get("triage_rationale", "LLM evaluated incident triage.")
            }

        fallback_data = self.deterministic_triage(incident_data)
        return {
            "success": True,
            "data": fallback_data,
            "mode": "DETERMINISTIC_ENGINE",
            "tokens": 0,
            "explanation": fallback_data["triage_rationale"]
        }
