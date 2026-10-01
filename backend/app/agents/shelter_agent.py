import logging
from typing import Dict, Any, List
from backend.app.agents.gemini_client import gemini_client
from backend.app.services.routing_engine import haversine_distance

logger = logging.getLogger("resq.agent.shelter")

SYSTEM_INSTRUCTION = """
You are the Shelter and Capacity Agent for RESQ.
Select the safest and most capable evacuation shelter based on real available headroom,
medical facility support, and proximity to the disaster zone.
Return JSON:
{
  "target_shelter_id": "string",
  "shelter_name": "string",
  "allocated_headcount": integer,
  "shelter_justification": "string",
  "contingency_shelter_id": "string"
}
"""

class ShelterCapacityAgent:
    def __init__(self):
        self.name = "Shelter and Capacity Agent"

    def deterministic_select(
        self,
        incident_lat: float,
        incident_lng: float,
        headcount_to_evacuate: int,
        requires_medical: bool,
        shelters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Deterministic selection considering headroom, medical capability, and distance.
        """
        viable = []
        for s in shelters:
            free_beds = s["total_capacity"] - s["current_occupancy"]
            if free_beds >= headcount_to_evacuate and s["status"] != "CLOSED":
                dist = haversine_distance(incident_lat, incident_lng, s["latitude"], s["longitude"])
                # Medical score bonus
                med_score = 10 if (requires_medical and s["has_medical_facility"]) else 0
                viable.append({
                    "shelter": s,
                    "distance_km": dist,
                    "free_beds": free_beds,
                    "score": dist - (med_score * 0.5)
                })

        if not viable:
            # Fallback to largest capacity shelter
            sorted_by_cap = sorted(shelters, key=lambda s: s["total_capacity"] - s["current_occupancy"], reverse=True)
            chosen = sorted_by_cap[0]
            dist = haversine_distance(incident_lat, incident_lng, chosen["latitude"], chosen["longitude"])
            justification = f"Emergency overflow allocation: Selected {chosen['name']} despite tight headroom."
            return {
                "target_shelter_id": chosen["id"],
                "shelter_name": chosen["name"],
                "allocated_headcount": headcount_to_evacuate,
                "distance_km": round(dist, 2),
                "remaining_capacity_after": max(0, (chosen["total_capacity"] - chosen["current_occupancy"]) - headcount_to_evacuate),
                "has_medical_support": chosen["has_medical_facility"],
                "shelter_justification": justification
            }

        viable.sort(key=lambda x: x["score"])
        primary = viable[0]["shelter"]
        p_dist = viable[0]["distance_km"]
        remaining = (primary["total_capacity"] - primary["current_occupancy"]) - headcount_to_evacuate

        justification = (
            f"Selected {primary['name']} ({round(p_dist, 1)} km from scene). "
            f"Current occupancy: {primary['current_occupancy']}/{primary['total_capacity']}. "
            f"Headroom safely absorbs {headcount_to_evacuate} evacuees leaving {remaining} slots. "
            f"Medical support: {'Active field clinic' if primary['has_medical_facility'] else 'Standard first-aid'}."
        )

        return {
            "target_shelter_id": primary["id"],
            "shelter_name": primary["name"],
            "allocated_headcount": headcount_to_evacuate,
            "distance_km": round(p_dist, 2),
            "remaining_capacity_after": remaining,
            "has_medical_support": primary["has_medical_facility"],
            "shelter_justification": justification
        }

    async def execute(
        self,
        incident_lat: float,
        incident_lng: float,
        headcount_to_evacuate: int,
        requires_medical: bool,
        shelters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        fallback_data = self.deterministic_select(
            incident_lat, incident_lng, headcount_to_evacuate, requires_medical, shelters
        )

        prompt = f"""
Disaster Location: [{incident_lat}, {incident_lng}]
Headcount to Evacuate: {headcount_to_evacuate}
Medical Critical Priority: {requires_medical}
Available Shelters:
{[ {'id': s['id'], 'name': s['name'], 'capacity': f"{s['current_occupancy']}/{s['total_capacity']}", 'medical': s['has_medical_facility']} for s in shelters ]}

Explain the humanitarian intake rationale and why {fallback_data['shelter_name']} was designated.
"""
        success, parsed, mode, tokens = await gemini_client.generate_structured(
            system_instruction=SYSTEM_INSTRUCTION,
            prompt=prompt
        )

        if success and parsed.get("shelter_justification"):
            fallback_data["shelter_justification"] = parsed["shelter_justification"]

        return {
            "success": True,
            "data": fallback_data,
            "mode": mode if success else "DETERMINISTIC_ENGINE",
            "tokens": tokens if success else 0,
            "explanation": fallback_data["shelter_justification"]
        }
