"""WebSocket endpoints and connection management routes."""

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.schemas.websocket import (
    WSBroadcastRequest,
    WSBroadcastResponse,
    WSStatusResponse,
)
from app.services.websocket_manager import ConnectionManager, manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSockets"])


def get_websocket_manager() -> ConnectionManager:
    """Dependency provider for ConnectionManager."""
    return manager


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    ws_manager: ConnectionManager = Depends(get_websocket_manager),
) -> None:
    """WebSocket connection endpoint for real-time notifications and messaging."""
    await ws_manager.connect(client_id, websocket)

    now_iso = datetime.now(timezone.utc).isoformat()

    # Welcome the connected client
    await ws_manager.send_personal_message(
        {
            "event": "CONNECTED",
            "client_id": "system",
            "timestamp": now_iso,
            "data": {
                "message": f"Welcome {client_id}! Connected to Real-Time Media Hub.",
                "client_id": client_id,
            },
        },
        client_id,
    )

    # Broadcast client joined event
    await ws_manager.broadcast(
        {
            "event": "CLIENT_JOINED",
            "client_id": client_id,
            "timestamp": now_iso,
            "data": {
                "client_id": client_id,
                "active_connections": ws_manager.get_active_count(),
            },
        },
        exclude_client=client_id,
    )

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                payload = json.loads(raw_text)
            except json.JSONDecodeError:
                payload = {"action": "message", "content": raw_text}

            action = payload.get("action", "message")
            content = payload.get("content", "")
            current_time = datetime.now(timezone.utc).isoformat()

            if action == "ping":
                await ws_manager.send_personal_message(
                    {
                        "event": "PONG",
                        "client_id": "system",
                        "timestamp": current_time,
                        "data": {"status": "ok"},
                    },
                    client_id,
                )
            elif action in ("chat", "broadcast", "message"):
                await ws_manager.broadcast(
                    {
                        "event": "CHAT_MESSAGE",
                        "client_id": client_id,
                        "timestamp": current_time,
                        "data": {"message": content, "sender": client_id},
                    }
                )
            else:
                await ws_manager.send_personal_message(
                    {
                        "event": "UNKNOWN_ACTION",
                        "client_id": "system",
                        "timestamp": current_time,
                        "data": {"action": action},
                    },
                    client_id,
                )

    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)
        leave_time = datetime.now(timezone.utc).isoformat()
        await ws_manager.broadcast(
            {
                "event": "CLIENT_LEFT",
                "client_id": client_id,
                "timestamp": leave_time,
                "data": {
                    "client_id": client_id,
                    "active_connections": ws_manager.get_active_count(),
                },
            }
        )
    except Exception as exc:
        logger.error(f"WebSocket error for client {client_id}: {exc}")
        await ws_manager.disconnect(client_id)


@router.get(
    "/api/ws/status",
    response_model=WSStatusResponse,
    summary="Get active WebSocket status",
    description="Returns current active WebSocket connection count and connected client IDs.",
)
async def get_websocket_status(
    ws_manager: ConnectionManager = Depends(get_websocket_manager),
) -> WSStatusResponse:
    """Return status of active WebSocket connections."""
    return WSStatusResponse(
        active_connections=ws_manager.get_active_count(),
        client_ids=ws_manager.get_active_clients(),
    )


@router.post(
    "/api/ws/broadcast",
    response_model=WSBroadcastResponse,
    summary="Broadcast message to connected WebSocket clients",
    description=(
        "Trigger a real-time broadcast message to all currently connected "
        "WebSocket clients directly via HTTP (ideal for testing in Swagger UI)."
    ),
)
async def broadcast_message(
    payload: WSBroadcastRequest,
    ws_manager: ConnectionManager = Depends(get_websocket_manager),
) -> WSBroadcastResponse:
    """Send a broadcast notification to all connected WebSocket subscribers."""
    now_iso = datetime.now(timezone.utc).isoformat()
    count = await ws_manager.broadcast(
        {
            "event": payload.event,
            "client_id": payload.sender,
            "timestamp": now_iso,
            "data": {"message": payload.message, "sender": payload.sender},
        }
    )
    return WSBroadcastResponse(
        status="broadcast_sent",
        recipients_count=count,
        broadcasted_at=now_iso,
        event=payload.event,
    )
