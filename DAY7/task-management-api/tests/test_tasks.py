# ==========================================
# TASK TESTS
# ==========================================


def get_auth_headers(client):

    client.post(
        "/api/auth/register",
        json={
            "username": "taskuser",
            "email": "task@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/api/auth/login",
        data={
            "username": "task@example.com",
            "password": "password123"
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def create_test_project(client, headers):

    response = client.post(
        "/api/projects/",
        json={
            "name": "Task Project",
            "description": "Project for task testing"
        },
        headers=headers
    )

    return response.json()["id"]


def test_create_task(client):

    headers = get_auth_headers(client)

    project_id = create_test_project(
        client,
        headers
    )

    response = client.post(
        f"/api/tasks/?project_id={project_id}",
        json={
            "title": "Test FastAPI",
            "description": "Learn testing",
            "priority": "high",
            "due_date": "2026-09-30"
        },
        headers=headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Test FastAPI"
    assert data["priority"] == "high"
    assert data["status"] == "pending"
    assert data["project_id"] == project_id


def test_get_tasks(client):

    headers = get_auth_headers(client)

    project_id = create_test_project(
        client,
        headers
    )

    client.post(
        f"/api/tasks/?project_id={project_id}",
        json={
            "title": "Task One",
            "description": "First task",
            "priority": "medium"
        },
        headers=headers
    )

    response = client.get(
        "/api/tasks/",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_filter_tasks_by_status(client):

    headers = get_auth_headers(client)

    project_id = create_test_project(
        client,
        headers
    )

    response = client.post(
        f"/api/tasks/?project_id={project_id}",
        json={
            "title": "Pending Task",
            "description": "Pending task",
            "priority": "low"
        },
        headers=headers
    )

    assert response.status_code == 201

    response = client.get(
        "/api/tasks/?status=pending",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    for task in data:
        assert task["status"] == "pending"


def test_update_task(client):

    headers = get_auth_headers(client)

    project_id = create_test_project(
        client,
        headers
    )

    create_response = client.post(
        f"/api/tasks/?project_id={project_id}",
        json={
            "title": "Old Task",
            "description": "Old description",
            "priority": "medium"
        },
        headers=headers
    )

    task_id = create_response.json()["id"]

    response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "status": "completed",
            "priority": "high"
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated Task"
    assert data["status"] == "completed"
    assert data["priority"] == "high"


def test_delete_task(client):

    headers = get_auth_headers(client)

    project_id = create_test_project(
        client,
        headers
    )

    create_response = client.post(
        f"/api/tasks/?project_id={project_id}",
        json={
            "title": "Delete Task",
            "description": "Task to delete",
            "priority": "low"
        },
        headers=headers
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/api/tasks/{task_id}",
        headers=headers
    )

    assert response.status_code == 204