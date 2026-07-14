from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Keeps track of all actively connected WebSocket clients
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 New client connected to live prediction feed. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"🔌 Client disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Pushes real-time prediction updates to all active UI subscribers."""
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Catch broken connections gracefully if a browser tab is abruptly closed
                disconnected_clients.append(connection)
                
        # Clean up stale connections
        for client in disconnected_clients:
            self.disconnect(client)

# Instantiate the global manager to be imported inside our prediction paths
manager = ConnectionManager()

@router.websocket("/ws/predictions")
async def websocket_endpoint(websocket: WebSocket):
    """The central WebSocket gateway specified by the upgrade blueprint[cite: 1]."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the channel alive. We are primarily broadcasting downstream,
            # but this listens for incoming frame heartbeats/pings.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)