"""Integration tests for WebSocket communication and Swagger broadcast."""

from fastapi.testclient import TestClient


def test_websocket_status_endpoint(client: TestClient) -> None:
    """Test /api/ws/status endpoint."""
    res = client.get("/api/ws/status")
    assert res.status_code == 200
    data = res.json()
    assert "active_connections" in data
    assert "client_ids" in data
    assert data["active_connections"] == 0


def test_http_broadcast_endpoint(client: TestClient) -> None:
    """Test broadcasting to connected clients via POST /api/ws/broadcast."""
    with client.websocket_connect("/ws/broadcast_listener") as ws:
        _ = ws.receive_json()  # welcome message

        # Broadcast via HTTP / Swagger endpoint
        payload = {
            "event": "SWAGGER_ALERT",
            "message": "Testing from Swagger UI",
            "sender": "swagger_admin",
        }
        res = client.post("/api/ws/broadcast", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "broadcast_sent"
        assert data["recipients_count"] == 1
        assert data["event"] == "SWAGGER_ALERT"

        # Verify WebSocket received the broadcast
        ws_msg = ws.receive_json()
        assert ws_msg["event"] == "SWAGGER_ALERT"
        assert ws_msg["client_id"] == "swagger_admin"
        assert ws_msg["data"]["message"] == "Testing from Swagger UI"


def test_websocket_connect_and_ping(client: TestClient) -> None:
    """Test connecting and pinging server."""
    with client.websocket_connect("/ws/tester_1") as ws:
        # Welcome
        msg = ws.receive_json()
        assert msg["event"] == "CONNECTED"
        assert msg["data"]["client_id"] == "tester_1"

        # Check status endpoint shows active connection
        status_res = client.get("/api/ws/status")
        assert status_res.json()["active_connections"] == 1
        assert "tester_1" in status_res.json()["client_ids"]

        # Ping
        ws.send_json({"action": "ping"})
        pong = ws.receive_json()
        assert pong["event"] == "PONG"
        assert pong["data"]["status"] == "ok"


def test_websocket_unknown_action(client: TestClient) -> None:
    """Test handling unknown action."""
    with client.websocket_connect("/ws/tester_2") as ws:
        _ = ws.receive_json()  # Consume welcome
        ws.send_json({"action": "custom_unknown"})
        resp = ws.receive_json()
        assert resp["event"] == "UNKNOWN_ACTION"
        assert resp["data"]["action"] == "custom_unknown"


def test_websocket_plain_text_message(client: TestClient) -> None:
    """Test handling raw text input that is not JSON."""
    with client.websocket_connect("/ws/tester_raw") as ws:
        _ = ws.receive_json()  # Consume welcome
        ws.send_text("hello raw message")
        msg = ws.receive_json()
        assert msg["event"] == "CHAT_MESSAGE"
        assert msg["data"]["message"] == "hello raw message"


def test_websocket_multi_client_broadcast_and_disconnect(client: TestClient) -> None:
    """Test real-time events between multiple clients."""
    with client.websocket_connect("/ws/alice") as ws_alice:
        welcome_alice = ws_alice.receive_json()
        assert welcome_alice["event"] == "CONNECTED"

        with client.websocket_connect("/ws/bob") as ws_bob:
            welcome_bob = ws_bob.receive_json()
            assert welcome_bob["event"] == "CONNECTED"

            # Alice receives notification that Bob joined
            joined_notice = ws_alice.receive_json()
            assert joined_notice["event"] == "CLIENT_JOINED"
            assert joined_notice["client_id"] == "bob"

            # Bob sends a chat broadcast
            ws_bob.send_json({"action": "chat", "content": "Hello Alice!"})

            # Alice receives Bob's chat
            chat_alice = ws_alice.receive_json()
            assert chat_alice["event"] == "CHAT_MESSAGE"
            assert chat_alice["client_id"] == "bob"
            assert chat_alice["data"]["message"] == "Hello Alice!"

            # Bob also receives his own broadcast
            chat_bob = ws_bob.receive_json()
            assert chat_bob["event"] == "CHAT_MESSAGE"
            assert chat_bob["data"]["message"] == "Hello Alice!"

        # Bob has now disconnected
        leave_notice = ws_alice.receive_json()
        assert leave_notice["event"] == "CLIENT_LEFT"
        assert leave_notice["client_id"] == "bob"
