"""Unit tests for WebSocket ConnectionManager."""

from unittest.mock import AsyncMock

import pytest

from app.services.websocket_manager import ConnectionManager


@pytest.mark.asyncio
async def test_connect_and_disconnect() -> None:
    """Test connecting and disconnecting clients."""
    manager = ConnectionManager()
    mock_ws = AsyncMock()

    await manager.connect("user1", mock_ws)
    mock_ws.accept.assert_awaited_once()
    assert manager.get_active_count() == 1
    assert "user1" in manager.get_active_clients()

    await manager.disconnect("user1")
    assert manager.get_active_count() == 0
    assert "user1" not in manager.get_active_clients()


@pytest.mark.asyncio
async def test_duplicate_connect_replaces_old() -> None:
    """Test reconnecting with same client_id closes previous socket."""
    manager = ConnectionManager()
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()

    await manager.connect("user1", mock_ws1)
    await manager.connect("user1", mock_ws2)

    mock_ws1.close.assert_awaited_once_with(code=1000)
    assert manager.get_active_count() == 1
    assert manager.active_connections["user1"] is mock_ws2


@pytest.mark.asyncio
async def test_send_personal_message_success() -> None:
    """Test sending personal message to connected client."""
    manager = ConnectionManager()
    mock_ws = AsyncMock()
    await manager.connect("user1", mock_ws)

    result = await manager.send_personal_message({"msg": "hello"}, "user1")
    assert result is True
    mock_ws.send_json.assert_awaited_once_with({"msg": "hello"})


@pytest.mark.asyncio
async def test_send_personal_message_unknown_client() -> None:
    """Test sending personal message to unknown client returns False."""
    manager = ConnectionManager()
    result = await manager.send_personal_message({"msg": "hello"}, "unknown")
    assert result is False


@pytest.mark.asyncio
async def test_send_personal_message_error_disconnects() -> None:
    """Test exception during personal message disconnects the failed client."""
    manager = ConnectionManager()
    mock_ws = AsyncMock()
    mock_ws.send_json.side_effect = RuntimeError("Broken pipe")
    await manager.connect("user1", mock_ws)

    result = await manager.send_personal_message({"msg": "hello"}, "user1")
    assert result is False
    assert manager.get_active_count() == 0


@pytest.mark.asyncio
async def test_broadcast_to_multiple_clients() -> None:
    """Test broadcasting message to all connected clients."""
    manager = ConnectionManager()
    ws1, ws2, ws3 = AsyncMock(), AsyncMock(), AsyncMock()

    await manager.connect("u1", ws1)
    await manager.connect("u2", ws2)
    await manager.connect("u3", ws3)

    msg = {"event": "TEST", "data": "all"}
    sent_count = await manager.broadcast(msg)

    assert sent_count == 3
    ws1.send_json.assert_awaited_once_with(msg)
    ws2.send_json.assert_awaited_once_with(msg)
    ws3.send_json.assert_awaited_once_with(msg)


@pytest.mark.asyncio
async def test_broadcast_with_exclusion() -> None:
    """Test broadcasting excluding sender client."""
    manager = ConnectionManager()
    ws1, ws2 = AsyncMock(), AsyncMock()

    await manager.connect("u1", ws1)
    await manager.connect("u2", ws2)

    msg = {"event": "TEST"}
    sent_count = await manager.broadcast(msg, exclude_client="u1")

    assert sent_count == 1
    ws1.send_json.assert_not_awaited()
    ws2.send_json.assert_awaited_once_with(msg)


@pytest.mark.asyncio
async def test_broadcast_cleans_up_dead_clients() -> None:
    """Test broadcast automatically prunes dead/broken connections."""
    manager = ConnectionManager()
    good_ws = AsyncMock()
    dead_ws = AsyncMock()
    dead_ws.send_json.side_effect = ConnectionResetError("Client dropped")

    await manager.connect("good", good_ws)
    await manager.connect("dead", dead_ws)

    sent = await manager.broadcast({"event": "TEST"})
    assert sent == 1
    assert manager.get_active_count() == 1
    assert "dead" not in manager.get_active_clients()


@pytest.mark.asyncio
async def test_close_all() -> None:
    """Test closing all connections during shutdown."""
    manager = ConnectionManager()
    ws1, ws2 = AsyncMock(), AsyncMock()

    await manager.connect("u1", ws1)
    await manager.connect("u2", ws2)

    await manager.close_all()
    assert manager.get_active_count() == 0
    ws1.close.assert_awaited_once_with(code=1001)
    ws2.close.assert_awaited_once_with(code=1001)
