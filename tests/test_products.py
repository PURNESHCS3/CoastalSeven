def test_create_product(
    client,
    auth_headers
):

    response = client.post(
        "/api/products/",
        headers=auth_headers,
        json={
            "name": "Laptop",
            "description": "Test laptop",
            "price": 50000,
            "stock": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Laptop"
    assert data["stock"] == 10


def test_get_products(
    client,
    test_product
):

    response = client.get(
        "/api/products/"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1


def test_get_product(
    client,
    test_product
):

    response = client.get(
        f"/api/products/{test_product.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_product.id


def test_get_nonexistent_product(client):

    response = client.get(
        "/api/products/99999"
    )

    assert response.status_code == 404


def test_update_product(
    client,
    test_product,
    auth_headers
):

    response = client.put(
        f"/api/products/{test_product.id}",
        headers=auth_headers,
        json={
            "name": "Updated Product",
            "description": "Updated description",
            "price": 150,
            "stock": 30
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Product"
    assert data["price"] == 150


def test_delete_product(
    client,
    test_product,
    auth_headers
):

    response = client.delete(
        f"/api/products/{test_product.id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert "message" in data


def test_products_require_auth_for_modification(
    client,
    test_product
):

    response = client.put(
        f"/api/products/{test_product.id}",
        json={
            "name": "Unauthorized Update",
            "description": "Test",
            "price": 100,
            "stock": 10
        }
    )

    assert response.status_code == 401