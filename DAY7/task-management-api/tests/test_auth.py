# ==========================================
# AUTHENTICATION TESTS
# ==========================================


def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True


def test_login_user(client):
    # Register user first
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123"
        }
    )

    assert register_response.status_code == 201

    # Login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "login@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password(client):
    # Register user
    client.post(
        "/api/auth/register",
        json={
            "username": "wrongpassword",
            "email": "wrong@example.com",
            "password": "password123"
        }
    )

    # Try wrong password
    response = client.post(
        "/api/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401