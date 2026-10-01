import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("resq.events")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """
        Broadcast typed event to all active clients.
        Events:
        - incident.created
        - incident.updated
        - resource.updated
        - route.updated
        - shelter.updated
        - agent.started
        - agent.completed
        - agent.failed
        - response_plan.created
        - response_plan.updated
        - verification.completed
        - dispatch.approved
        - simulation.event
        """
        message = json.dumps({
            "type": event_type,
            "data": data
        })
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                dead_connections.append(connection)
        
        for dead in dead_connections:
            self.disconnect(dead)

event_manager = ConnectionManager()
