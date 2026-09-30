from unittest.mock import MagicMock


def test_create_order(
    client,
    test_product,
    auth_headers,
    monkeypatch
):

    client.post(
        "/api/cart/add",
        headers=auth_headers,
        json={
            "product_id": test_product.id,
            "quantity": 2
        }
    )

    mock_task = MagicMock()

    monkeypatch.setattr(
        "app.routers.orders.send_order_confirmation_email",
        mock_task
    )

    response = client.post(
        "/api/orders/",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Order placed successfully"
    assert data["status"] == "confirmed"
    assert data["order_id"] > 0


def test_order_empty_cart(
    client,
    auth_headers
):

    response = client.post(
        "/api/orders/",
        headers=auth_headers
    )

    assert response.status_code == 400

    assert response.json()["detail"] == "Cart is empty"


def test_get_orders(
    client,
    auth_headers
):

    response = client.get(
        "/api/orders/",
        headers=auth_headers
    )

    assert response.status_code == 200


def test_get_nonexistent_order(
    client,
    auth_headers
):

    response = client.get(
        "/api/orders/99999",
        headers=auth_headers
    )

    assert response.status_code == 404


def test_order_reduces_stock(
    client,
    test_product,
    auth_headers,
    db,
    monkeypatch
):

    original_stock = test_product.stock

    client.post(
        "/api/cart/add",
        headers=auth_headers,
        json={
            "product_id": test_product.id,
            "quantity": 2
        }
    )

    mock_task = MagicMock()

    monkeypatch.setattr(
        "app.routers.orders.send_order_confirmation_email",
        mock_task
    )

    response = client.post(
        "/api/orders/",
        headers=auth_headers
    )

    assert response.status_code == 200

    db.refresh(test_product)

    assert test_product.stock == original_stock - 2