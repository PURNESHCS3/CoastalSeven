"""API integration tests for /api/upload endpoints."""

from fastapi.testclient import TestClient


def test_upload_valid_png(client: TestClient, sample_png_bytes: bytes) -> None:
    """Test successful PNG upload and variant generation."""
    files = {"file": ("test_avatar.png", sample_png_bytes, "image/png")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "test_avatar.png"
    assert data["content_type"] == "image/png"
    assert data["width"] == 800
    assert data["height"] == 600
    assert "thumbnail" in data["variants"]
    assert "medium" in data["variants"]
    assert data["variants"]["thumbnail"]["width"] <= 150
    assert data["variants"]["medium"]["width"] <= 600

    # Verify static file access
    thumb_url = data["variants"]["thumbnail"]["url"]
    static_res = client.get(thumb_url)
    assert static_res.status_code == 200


def test_upload_valid_jpeg(client: TestClient, sample_jpeg_bytes: bytes) -> None:
    """Test successful JPEG upload."""
    files = {"file": ("banner.jpg", sample_jpeg_bytes, "image/jpeg")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "banner.jpg"
    assert data["content_type"] == "image/jpeg"
    assert data["width"] == 1000
    assert data["height"] == 800


def test_list_and_get_uploaded_images(
    client: TestClient, sample_png_bytes: bytes
) -> None:
    """Test GET /api/upload and GET /api/upload/{filename}."""
    # 1. Upload an image
    files = {"file": ("gallery_pic.png", sample_png_bytes, "image/png")}
    upload_res = client.post("/api/upload", files=files)
    assert upload_res.status_code == 201
    saved_filename = upload_res.json()["filename"]

    # 2. List images
    list_res = client.get("/api/upload")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total_images"] >= 1
    matching = [img for img in list_data["images"] if img["filename"] == saved_filename]
    assert len(matching) == 1

    # 3. Get single image details
    detail_res = client.get(f"/api/upload/{saved_filename}")
    assert detail_res.status_code == 200
    assert detail_res.json()["filename"] == saved_filename

    # 4. Get non-existent image details returns 404
    missing_res = client.get("/api/upload/non_existent.png")
    assert missing_res.status_code == 404


def test_delete_uploaded_image(client: TestClient, sample_png_bytes: bytes) -> None:
    """Test DELETE /api/upload/{filename}."""
    # 1. Upload an image to delete
    files = {"file": ("to_delete.png", sample_png_bytes, "image/png")}
    upload_res = client.post("/api/upload", files=files)
    saved_filename = upload_res.json()["filename"]

    # 2. Delete it
    del_res = client.delete(f"/api/upload/{saved_filename}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # 3. Verify it is now gone
    get_res = client.get(f"/api/upload/{saved_filename}")
    assert get_res.status_code == 404

    # 4. Deleting non-existent file returns 404
    del_missing = client.delete("/api/upload/never_existed.png")
    assert del_missing.status_code == 404


def test_upload_unsupported_extension(
    client: TestClient, sample_png_bytes: bytes
) -> None:
    """Test upload fails with 415 on unsupported extension."""
    files = {"file": ("script.sh", sample_png_bytes, "image/png")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 415
    assert "Extension '.sh' is not supported" in response.json()["detail"]


def test_upload_unsupported_mime(client: TestClient, sample_png_bytes: bytes) -> None:
    """Test upload fails with 415 on unsupported MIME type."""
    files = {"file": ("valid.png", sample_png_bytes, "application/pdf")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 415
    assert (
        "Content type 'application/pdf' is not supported" in response.json()["detail"]
    )


def test_upload_corrupted_image(
    client: TestClient, corrupted_image_bytes: bytes
) -> None:
    """Test upload fails with 400 when file is corrupt or spoofed."""
    files = {"file": ("corrupt.png", corrupted_image_bytes, "image/png")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 400
    assert "failed image verification" in response.json()["detail"]


def test_upload_oversize_image(client: TestClient, oversize_image_bytes: bytes) -> None:
    """Test upload fails with 413 when file exceeds 5MB."""
    files = {"file": ("large.png", oversize_image_bytes, "image/png")}
    response = client.post("/api/upload", files=files)

    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["detail"]


def test_upload_triggers_websocket_broadcast(
    client: TestClient, sample_png_bytes: bytes
) -> None:
    """Test that uploading an image sends real-time broadcast to connected WebSocket."""
    with client.websocket_connect("/ws/listener_client") as ws:
        # 1. First event is welcome CONNECTED
        welcome = ws.receive_json()
        assert welcome["event"] == "CONNECTED"

        # 2. Upload file
        files = {"file": ("realtime.png", sample_png_bytes, "image/png")}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 201

        # 3. WebSocket client should receive IMAGE_UPLOADED event
        event = ws.receive_json()
        assert event["event"] == "IMAGE_UPLOADED"
        assert event["data"]["original_filename"] == "realtime.png"
        assert "thumbnail" in event["data"]["variants"]
