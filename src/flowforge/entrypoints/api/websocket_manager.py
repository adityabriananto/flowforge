from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps workflow instance_id (str) to a list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, instance_id: str, websocket: WebSocket):
        await websocket.accept()
        if instance_id not in self.active_connections:
            self.active_connections[instance_id] = []
        self.active_connections[instance_id].append(websocket)

    def disconnect(self, instance_id: str, websocket: WebSocket):
        if instance_id in self.active_connections:
            if websocket in self.active_connections[instance_id]:
                self.active_connections[instance_id].remove(websocket)
            if not self.active_connections[instance_id]:
                del self.active_connections[instance_id]

    async def broadcast_to_instance(self, instance_id: str, message: dict):
        """Send message JSON to all WebSockets listening to this instance."""
        if instance_id in self.active_connections:
            for connection in self.active_connections[instance_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection might be dead, disconnect will handle clean up or we ignore send failure
                    pass

# Singleton manager
ws_manager = ConnectionManager()
