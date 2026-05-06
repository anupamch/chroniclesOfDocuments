from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Map of client_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        print(f"[WS] Client {client_id} connected. Total: {len(self.active_connections[client_id])}")

    def disconnect(self, client_id: str, websocket: WebSocket):
        if client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        print(f"[WS] Client {client_id} disconnected.")

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"[WS] Error sending message to {client_id}: {e}")

    async def broadcast(self, message: dict):
        for client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"[WS] Error broadcasting to {client_id}: {e}")


# Global instance
manager = ConnectionManager()
