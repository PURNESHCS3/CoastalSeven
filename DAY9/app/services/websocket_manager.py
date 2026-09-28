"""WebSocket connection manager for real-time notifications."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections and handles broadcasts."""

    def __init__(self) -> None:
        self.active_connections: Dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        """Accept WebSocket connection and register client."""
        await websocket.accept()
        async with self._lock:
            # If client_id is already connected, close old connection first
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].close(code=1000)
                except Exception:
                    pass
            self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}")

    async def disconnect(self, client_id: str) -> None:
        """Unregister a client connection."""
        async with self._lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                logger.info(f"WebSocket client disconnected: {client_id}")

    async def send_personal_message(
        self, message: Dict[str, Any], client_id: str
    ) -> bool:
        """Send a JSON message to a specific client. Returns True if successful."""
        websocket: Optional[WebSocket] = None
        async with self._lock:
            websocket = self.active_connections.get(client_id)

        if websocket is None:
            return False

        try:
            await websocket.send_json(message)
            return True
        except Exception as exc:
            logger.warning(f"Failed to send personal message to {client_id}: {exc}")
            await self.disconnect(client_id)
            return False

    async def broadcast(
        self, message: Dict[str, Any], exclude_client: Optional[str] = None
    ) -> int:
        """Broadcast a message to all active clients except optional excluded client.

        Returns number of clients successfully received the message.
        """
        async with self._lock:
            recipients = [
                (cid, ws)
                for cid, ws in self.active_connections.items()
                if cid != exclude_client
            ]

        successful_count = 0
        dead_clients: List[str] = []

        for cid, ws in recipients:
            try:
                await ws.send_json(message)
                successful_count += 1
            except Exception as exc:
                logger.warning(
                    f"Broadcast failed for client {cid}: {exc}. Marking for removal."
                )
                dead_clients.append(cid)

        # Cleanup any dead clients
        if dead_clients:
            async with self._lock:
                for dead_cid in dead_clients:
                    self.active_connections.pop(dead_cid, None)

        return successful_count

    def get_active_count(self) -> int:
        """Return the current count of active connections."""
        return len(self.active_connections)

    def get_active_clients(self) -> List[str]:
        """Return list of connected client IDs."""
        return list(self.active_connections.keys())

    async def close_all(self) -> None:
        """Close all active connections during shutdown."""
        async with self._lock:
            for cid, ws in list(self.active_connections.items()):
                try:
                    await ws.close(code=1001)
                except Exception:
                    pass
            self.active_connections.clear()


# Global singleton instance for connection management
manager = ConnectionManager()
