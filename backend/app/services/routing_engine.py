import math
import logging
from typing import List, Dict, Any, Optional, Tuple
import networkx as nx

logger = logging.getLogger("resq.routing")

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class RoutingEngine:
    """
    Authoritative Graph Routing Engine based on Suryanagar Road Network.
    Computes shortest paths, detects closures, and plans alternative hazard-avoidance routes.
    """
    
    def __init__(self, segments: List[Dict[str, Any]]):
        self.segments = segments
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        self.graph.clear()
        for seg in self.segments:
            start = seg["start_node"]
            end = seg["end_node"]
            length_km = seg["length_km"]
            speed_kmh = seg["speed_limit_kmh"]
            
            # Check blockage
            is_blocked = seg.get("is_blocked", False)
            if is_blocked:
                effective_speed = 0.001
                weight = 999999.0 # Effectively impassable
            else:
                effective_speed = max(10.0, speed_kmh)
                weight = (length_km / effective_speed) * 60.0 # Time in minutes
                
            self.graph.add_edge(
                start, end,
                code=seg["code"],
                name=seg["name"],
                length_km=length_km,
                speed_kmh=effective_speed,
                weight=weight,
                is_blocked=is_blocked,
                start_lat=seg["start_lat"],
                start_lng=seg["start_lng"],
                end_lat=seg["end_lat"],
                end_lng=seg["end_lng"]
            )

    def find_nearest_node(self, lat: float, lng: float) -> str:
        best_node = None
        min_dist = float("inf")
        
        # Check node positions from segments
        nodes = {}
        for seg in self.segments:
            nodes[seg["start_node"]] = (seg["start_lat"], seg["start_lng"])
            nodes[seg["end_node"]] = (seg["end_lat"], seg["end_lng"])
            
        for node, (nlat, nlng) in nodes.items():
            dist = haversine_distance(lat, lng, nlat, nlng)
            if dist < min_dist:
                min_dist = dist
                best_node = node
                
        return best_node or "SEC-6"

    def calculate_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        avoid_segments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculates optimal route between two points using the authoritative simulation graph.
        Returns distance, ETA, waypoints [[lat, lng]], and traversed segment codes.
        """
        origin_node = self.find_nearest_node(origin_lat, origin_lng)
        dest_node = self.find_nearest_node(dest_lat, dest_lng)
        
        # Create a working graph copy with temporary penalties if avoid_segments specified
        working_graph = self.graph.copy()
        if avoid_segments:
            for u, v, data in working_graph.edges(data=True):
                if data.get("code") in avoid_segments:
                    data["weight"] = 999999.0

        try:
            if origin_node == dest_node:
                # Direct route
                dist = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
                eta = max(1.0, (dist / 40.0) * 60.0)
                waypoints = [[origin_lat, origin_lng], [dest_lat, dest_lng]]
                return {
                    "path_found": True,
                    "nodes": [origin_node],
                    "segments": [],
                    "total_distance_km": round(dist, 2),
                    "estimated_eta_minutes": round(eta, 1),
                    "waypoints": waypoints
                }

            path_nodes = nx.shortest_path(working_graph, source=origin_node, target=dest_node, weight="weight")
            
            # Check if path contains blocked segments
            total_dist = 0.0
            total_time_min = 0.0
            segments_traversed = []
            waypoints = [[origin_lat, origin_lng]]
            
            for i in range(len(path_nodes) - 1):
                u, v = path_nodes[i], path_nodes[i+1]
                edge_data = working_graph[u][v]
                if edge_data["weight"] >= 99999.0:
                    # Traverses an impassable road
                    return {
                        "path_found": False,
                        "error": f"Road segment {edge_data.get('code')} is blocked and impassable."
                    }
                total_dist += edge_data["length_km"]
                total_time_min += edge_data["weight"]
                segments_traversed.append(edge_data["code"])
                
                # Add node waypoints with a gentle curve interpolation
                waypoints.append([edge_data["start_lat"], edge_data["start_lng"]])
                # Midpoint
                mid_lat = (edge_data["start_lat"] + edge_data["end_lat"]) / 2.0
                mid_lng = (edge_data["start_lng"] + edge_data["end_lng"]) / 2.0
                waypoints.append([mid_lat, mid_lng])
                waypoints.append([edge_data["end_lat"], edge_data["end_lng"]])
                
            waypoints.append([dest_lat, dest_lng])
            
            return {
                "path_found": True,
                "nodes": path_nodes,
                "segments": segments_traversed,
                "total_distance_km": round(total_dist, 2),
                "estimated_eta_minutes": round(total_time_min, 1),
                "waypoints": waypoints
            }
        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            logger.error(f"Routing failed between {origin_node} and {dest_node}: {e}")
            return {
                "path_found": False,
                "error": "No viable hazard-free route found between coordinates."
            }

    def check_route_invalidation(self, route_segments: List[str], blocked_segment_codes: List[str]) -> Tuple[bool, Optional[str]]:
        for seg in route_segments:
            if seg in blocked_segment_codes:
                return True, f"Primary route compromised: Road segment {seg} is blocked."
        return False, None
