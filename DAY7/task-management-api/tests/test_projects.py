# ==========================================
# PROJECT TESTS
# ==========================================


def get_auth_headers(client):
    # Register user
    client.post(
        "/api/auth/register",
        json={
            "username": "projectuser",
            "email": "project@example.com",
            "password": "password123"
        }
    )

    # Login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "project@example.com",
            "password": "password123"
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_create_project(client):

    headers = get_auth_headers(client)

    response = client.post(
        "/api/projects/",
        json={
            "name": "Test Project",
            "description": "Project created during testing"
        },
        headers=headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Project"
    assert data["description"] == (
        "Project created during testing"
    )


def test_get_projects(client):

    headers = get_auth_headers(client)

    # Create project
    client.post(
        "/api/projects/",
        json={
            "name": "Project One",
            "description": "First project"
        },
        headers=headers
    )

    response = client.get(
        "/api/projects/",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_update_project(client):

    headers = get_auth_headers(client)

    # Create project
    create_response = client.post(
        "/api/projects/",
        json={
            "name": "Old Project",
            "description": "Old description"
        },
        headers=headers
    )

    project_id = create_response.json()["id"]

    # Update project
    response = client.put(
        f"/api/projects/{project_id}",
        json={
            "name": "Updated Project",
            "description": "Updated description"
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Project"
    assert data["description"] == "Updated description"


def test_delete_project(client):

    headers = get_auth_headers(client)

    # Create project
    create_response = client.post(
        "/api/projects/",
        json={
            "name": "Delete Project",
            "description": "Project to delete"
        },
        headers=headers
    )

    project_id = create_response.json()["id"]

    # Delete project
    response = client.delete(
        f"/api/projects/{project_id}",
        headers=headers
    )

    assert response.status_code == 204