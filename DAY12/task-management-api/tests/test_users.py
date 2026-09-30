# ==========================================
# USER ROUTES TESTS
# ==========================================
import pytest
from app.models import User
from app.auth.jwt import hash_password, create_access_token


def get_user_token(client, username="normaluser", email="normal@example.com", role="user"):
    client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "password123"
        }
    )
    response = client.post(
        "/api/auth/login",
        data={
            "username": email,
            "password": "password123"
        }
    )
    return response.json()["access_token"]


def test_get_my_profile_unauthenticated(client):
    """Calling /api/users/me without token should be rejected."""
    response = client.get("/api/users/me")
    assert response.status_code in (401, 403)


def test_get_my_profile_invalid_token(client):
    """Calling /api/users/me with an invalid token should return 401."""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_get_my_profile_success(client):
    """Calling /api/users/me with valid token should return current user info without password."""
    token = get_user_token(client, username="alice", email="alice@example.com")
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "hashed_password" not in data
    assert "password" not in data


def test_get_my_profile_inactive_user(client, db_session):
    """Inactive users should be rejected with 400 Bad Request."""
    user = User(
        username="inactive_user",
        email="inactive@example.com",
        hashed_password=hash_password("password123"),
        role="user",
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(user_id=user.id)
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"


def test_get_users_list(client):
    """Calling /api/users/ with valid token should list all users."""
    token = get_user_token(client, username="bob", email="bob@example.com")
    response = client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1
    assert any(u["username"] == "bob" for u in users)


def test_get_users_unauthenticated(client):
    """Calling /api/users/ without auth should be rejected."""
    response = client.get("/api/users/")
    assert response.status_code in (401, 403)


def test_admin_route_forbidden_for_regular_user(client):
    """Regular user accessing /api/users/admin/all should receive 403 Forbidden."""
    token = get_user_token(client, username="regular_joe", email="joe@example.com")
    response = client.get(
        "/api/users/admin/all",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_route_success_for_admin(client, db_session):
    """Admin user accessing /api/users/admin/all should succeed with 200 OK."""
    admin = User(
        username="superadmin",
        email="admin@example.com",
        hashed_password=hash_password("adminpass123"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    admin_token = create_access_token(user_id=admin.id)
    response = client.get(
        "/api/users/admin/all",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(u["username"] == "superadmin" and u["role"] == "admin" for u in data)
