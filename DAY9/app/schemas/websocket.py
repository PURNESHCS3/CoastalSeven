"""WebSocket messaging and notification schemas."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class WSClientMessage(BaseModel):
    """Schema for messages incoming from WebSocket clients."""

    action: str = Field(..., description="Action name (e.g., ping, chat, broadcast)")
    content: Optional[str] = Field(None, description="Message body or payload")


class WSNotification(BaseModel):
    """Schema for outgoing WebSocket event notifications."""

    event: str = Field(
        ..., description="Event name (e.g., IMAGE_UPLOADED, CLIENT_JOINED)"
    )
    client_id: Optional[str] = Field(None, description="Sender client ID or 'system'")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    data: Any = Field(default=None, description="Notification payload")


class WSStatusResponse(BaseModel):
    """WebSocket server status response."""

    active_connections: int = Field(..., description="Total connected clients")
    client_ids: List[str] = Field(..., description="List of active client identifiers")


class WSBroadcastRequest(BaseModel):
    """Request model for sending a WebSocket broadcast via Swagger/REST."""

    event: str = Field(
        default="SERVER_ANNOUNCEMENT",
        description="Event name/identifier for connected clients",
    )
    message: str = Field(
        ..., description="Message text or payload content to broadcast"
    )
    sender: str = Field(
        default="swagger_tester",
        description="Sender identity tag",
    )


class WSBroadcastResponse(BaseModel):
    """Response model for broadcast trigger."""

    status: str = Field(..., description="Result status")
    recipients_count: int = Field(
        ..., description="Number of clients that received the broadcast"
    )
    broadcasted_at: str = Field(..., description="Timestamp of broadcast")
    event: str = Field(..., description="Broadcasted event name")
