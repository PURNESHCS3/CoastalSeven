def test_add_product_to_cart(
    client,
    test_product,
    auth_headers
):

    response = client.post(
        "/api/cart/add",
        headers=auth_headers,
        json={
            "product_id": test_product.id,
            "quantity": 2
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["cart"][str(test_product.id)] == 2


def test_get_cart(
    client,
    test_product,
    auth_headers
):

    client.post(
        "/api/cart/add",
        headers=auth_headers,
        json={
            "product_id": test_product.id,
            "quantity": 2
        }
    )

    response = client.get(
        "/api/cart/",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert str(test_product.id) in data["cart"]


def test_empty_cart(
    client,
    auth_headers
):

    response = client.get(
        "/api/cart/",
        headers=auth_headers
    )

    assert response.status_code == 200

    assert response.json()["cart"] == {}


def test_cart_insufficient_stock(
    client,
    test_product,
    auth_headers
):

    response = client.post(
        "/api/cart/add",
        headers=auth_headers,
        json={
            "product_id": test_product.id,
            "quantity": 999
        }
    )

    assert response.status_code == 400


def test_cart_invalid_product(
    client,
    auth_headers
):

    response = client.post(
        "/api/cart/add",
        headers=auth_headers,
        json={
            "product_id": 99999,
            "quantity": 1
        }
    )

    assert response.status_code == 404


def test_remove_product_from_cart(
    client,
    test_product,
    auth_headers
):

    client.post(
        "/api/cart/add",
        headers=auth_headers,
        json={
            "product_id": test_product.id,
            "quantity": 2
        }
    )

    response = client.delete(
        f"/api/cart/{test_product.id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert str(test_product.id) not in data["cart"]