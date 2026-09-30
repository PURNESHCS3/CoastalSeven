# ==========================================
# PROJECT TESTS (Admin & User Scenarios)
# ==========================================
from app.models import User
from app.auth.jwt import create_access_token, hash_password


def get_admin_headers(client, db_session):
    admin = User(
        username="admin_proj_user",
        email="admin_proj@example.com",
        hashed_password=hash_password("password123"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = create_access_token(user_id=admin.id)
    return {"Authorization": f"Bearer {token}"}, admin


def get_regular_headers(client, db_session):
    user = User(
        username="regular_proj_user",
        email="reg_proj@example.com",
        hashed_password=hash_password("password123"),
        role="user",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user_id=user.id)
    return {"Authorization": f"Bearer {token}"}, user


def test_regular_user_cannot_create_project(client, db_session):
    headers, _ = get_regular_headers(client, db_session)
    response = client.post(
        "/api/projects/",
        json={"name": "Forbidden Project", "description": "Should fail"},
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_create_project(client, db_session):
    headers, _ = get_admin_headers(client, db_session)
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
    assert data["description"] == "Project created during testing"


def test_get_projects(client, db_session):
    headers, _ = get_admin_headers(client, db_session)
    client.post(
        "/api/projects/",
        json={"name": "Project One", "description": "First project"},
        headers=headers
    )
    response = client.get("/api/projects/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_update_project(client, db_session):
    headers, _ = get_admin_headers(client, db_session)
    create_response = client.post(
        "/api/projects/",
        json={"name": "Old Project", "description": "Old description"},
        headers=headers
    )
    project_id = create_response.json()["id"]

    response = client.put(
        f"/api/projects/{project_id}",
        json={"name": "Updated Project", "description": "Updated description"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["description"] == "Updated description"


def test_regular_user_cannot_update_project(client, db_session):
    admin_headers, _ = get_admin_headers(client, db_session)
    user_headers, _ = get_regular_headers(client, db_session)
    create_response = client.post(
        "/api/projects/",
        json={"name": "Admin Project", "description": "Admin-managed"},
        headers=admin_headers
    )
    project_id = create_response.json()["id"]

    response = client.put(
        f"/api/projects/{project_id}",
        json={"name": "Unauthorized update"},
        headers=user_headers
    )
    assert response.status_code == 403


def test_admin_delete_project(client, db_session):
    headers, _ = get_admin_headers(client, db_session)
    create_response = client.post(
        "/api/projects/",
        json={"name": "Delete Project", "description": "Project to delete"},
        headers=headers
    )
    project_id = create_response.json()["id"]

    response = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert response.status_code == 204


def test_regular_user_cannot_delete_project(client, db_session):
    admin_headers, _ = get_admin_headers(client, db_session)
    reg_headers, _ = get_regular_headers(client, db_session)

    create_response = client.post(
        "/api/projects/",
        json={"name": "Admin Project", "description": "Only admin deletes"},
        headers=admin_headers
    )
    project_id = create_response.json()["id"]

    response = client.delete(f"/api/projects/{project_id}", headers=reg_headers)
    assert response.status_code == 403


def test_admin_assign_project_to_user(client, db_session):
    admin_headers, _ = get_admin_headers(client, db_session)
    reg_headers, reg_user = get_regular_headers(client, db_session)

    create_response = client.post(
        "/api/projects/",
        json={"name": "Assigned Project", "description": "To be assigned"},
        headers=admin_headers
    )
    project_id = create_response.json()["id"]

    # Assign user to project
    assign_res = client.post(
        f"/api/projects/{project_id}/assign",
        json={"user_id": reg_user.id},
        headers=admin_headers
    )
    assert assign_res.status_code == 200
    members = assign_res.json()["members"]
    assert any(m["id"] == reg_user.id for m in members)

    # Project members can view details but only see their own assigned tasks.
    view_res = client.get(f"/api/projects/{project_id}", headers=reg_headers)
    assert view_res.status_code == 200
    assert view_res.json()["name"] == "Assigned Project"

    tasks_res = client.get(
        f"/api/tasks/?project_id={project_id}",
        headers=reg_headers
    )
    assert tasks_res.status_code == 200
    assert tasks_res.json() == []

    task_res = client.post(
        f"/api/tasks/?project_id={project_id}",
        json={"title": "Assigned project task", "assignee_id": reg_user.id},
        headers=admin_headers
    )
    assert task_res.status_code == 201

    # Assigning a task makes it visible in the user's task list.
    view_res = client.get(f"/api/projects/{project_id}", headers=reg_headers)
    assert view_res.status_code == 200
    assert view_res.json()["name"] == "Assigned Project"

    tasks_res = client.get(
        f"/api/tasks/?project_id={project_id}",
        headers=reg_headers
    )
    assert tasks_res.status_code == 200
    assert [task["id"] for task in tasks_res.json()] == [task_res.json()["id"]]