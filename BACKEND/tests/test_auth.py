def test_register_user(client):

    response = client.post(
        "/api/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123"
        }
    )

    assert response.status_code in [200, 201]

    data = response.json()

    assert "email" in data
    assert data["role"] == "user"


def test_login_success(client, test_user):

    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client, test_user):

    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code in [400, 401]


def test_login_invalid_email(client):

    response = client.post(
        "/api/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "password123"
        }
    )

    assert response.status_code in [400, 401, 404, 422]


def test_protected_product_creation_without_token(
    client
):

    response = client.post(
        "/api/products/",
        json={
            "name": "Unauthorized Product",
            "description": "Test",
            "price": 100,
            "stock": 5
        }
    )

    assert response.status_code == 401