import logging
from typing import Dict, Any, List, Optional
from backend.app.agents.gemini_client import gemini_client
from backend.app.services.routing_engine import RoutingEngine

logger = logging.getLogger("resq.agent.route")

SYSTEM_INSTRUCTION = """
You are the Route Optimization Agent for RESQ.
Analyze calculated route options from the authoritative road graph,
assess hazard proximity, closures, and explain route safety tradeoffs.
Return JSON:
{
  "route_explanation": "string",
  "hazard_warnings": ["string"],
  "alternative_corridor_viable": boolean
}
"""

class RouteOptimizationAgent:
    def __init__(self):
        self.name = "Route Optimization Agent"

    async def execute(
        self,
        routing_engine: RoutingEngine,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        origin_name: str,
        dest_name: str,
        avoid_segments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes real graph routing calculation and enriches with agent hazard explanation.
        """
        route_result = routing_engine.calculate_route(
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            avoid_segments=avoid_segments
        )

        if not route_result.get("path_found"):
            explanation = f"Critical routing alert: No safe, unblocked route found from {origin_name} to {dest_name}."
            return {
                "success": False,
                "data": {
                    "path_found": False,
                    "error": route_result.get("error", "No route available"),
                    "route_explanation": explanation
                },
                "mode": "DETERMINISTIC_ENGINE",
                "tokens": 0,
                "explanation": explanation
            }

        dist = route_result["total_distance_km"]
        eta = route_result["estimated_eta_minutes"]
        segments = route_result["segments"]
        waypoints = route_result["waypoints"]

        explanation = (
            f"Calculated optimal emergency transit path: {dist} km via segments {', '.join(segments) or 'Direct'} "
            f"with estimated ETA of {eta} minutes. All traversed road segments verified clear of active closures."
        )

        prompt = f"""
Route details:
Origin: {origin_name} [{origin_lat}, {origin_lng}]
Destination: {dest_name} [{dest_lat}, {dest_lng}]
Distance: {dist} km | ETA: {eta} min
Segments: {segments}

Explain route security, speed tradeoffs, and driver caution points.
"""
        success, parsed, mode, tokens = await gemini_client.generate_structured(
            system_instruction=SYSTEM_INSTRUCTION,
            prompt=prompt
        )

        if success and parsed.get("route_explanation"):
            explanation = parsed["route_explanation"]

        return {
            "success": True,
            "data": {
                "path_found": True,
                "origin_name": origin_name,
                "destination_name": dest_name,
                "origin_lat": origin_lat,
                "origin_lng": origin_lng,
                "dest_lat": dest_lat,
                "dest_lng": dest_lng,
                "total_distance_km": dist,
                "estimated_eta_minutes": eta,
                "segments": segments,
                "waypoints": waypoints,
                "route_explanation": explanation
            },
            "mode": mode if success else "DETERMINISTIC_ENGINE",
            "tokens": tokens if success else 0,
            "explanation": explanation
        }
