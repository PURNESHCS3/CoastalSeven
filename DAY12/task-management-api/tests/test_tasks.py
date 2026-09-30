# ==========================================
# TASK TESTS
# ==========================================
from app.models import Project, Task, User
from app.auth.jwt import create_access_token, hash_password


def get_auth_headers(client, db_session):
    admin = User(
        username="task_admin_user",
        email="task_admin@example.com",
        hashed_password=hash_password("password123"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = create_access_token(user_id=admin.id)
    return {"Authorization": f"Bearer {token}"}


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


def test_create_task(client, db_session):
    headers = get_auth_headers(client, db_session)
    project_id = create_test_project(client, headers)

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


def test_get_tasks(client, db_session):
    headers = get_auth_headers(client, db_session)
    project_id = create_test_project(client, headers)

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


def test_user_can_only_list_assigned_tasks(client, db_session):
    owner = User(
        username="project_owner",
        email="owner@example.com",
        hashed_password="unused",
        role="user",
        is_active=True
    )
    assignee = User(
        username="task_assignee",
        email="assignee@example.com",
        hashed_password="unused",
        role="user",
        is_active=True
    )
    other_user = User(
        username="other_owner",
        email="other@example.com",
        hashed_password="unused",
        role="user",
        is_active=True
    )
    db_session.add_all([owner, assignee, other_user])
    db_session.commit()

    assigned_project = Project(name="Assigned project", owner_id=owner.id)
    company_project = Project(name="Company project", owner_id=other_user.id)
    company_project.members.append(assignee)
    private_project = Project(name="Private project", owner_id=other_user.id)
    db_session.add_all([assigned_project, company_project, private_project])
    db_session.commit()

    assigned_task = Task(
        title="Assigned to current user",
        project_id=assigned_project.id,
        assignee_id=assignee.id,
        priority="medium"
    )
    hidden_task = Task(
        title="Not assigned to current user",
        project_id=company_project.id,
        assignee_id=other_user.id,
        priority="medium"
    )
    db_session.add_all([assigned_task, hidden_task])
    db_session.commit()

    token = create_access_token(user_id=assignee.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/tasks/", headers=headers)
    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [assigned_task.id]

    response = client.get("/api/tasks/mine", headers=headers)
    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [assigned_task.id]

    response = client.get("/api/projects/", headers=headers)
    assert response.status_code == 200
    assert [project["id"] for project in response.json()] == [
        assigned_project.id,
        company_project.id,
        private_project.id
    ]

    response = client.get(f"/api/projects/{assigned_project.id}", headers=headers)
    assert response.status_code == 200

    response = client.get(f"/api/projects/{company_project.id}", headers=headers)
    assert response.status_code == 200

    response = client.get(f"/api/projects/{private_project.id}", headers=headers)
    assert response.status_code == 200

    response = client.get(f"/api/tasks/{hidden_task.id}", headers=headers)
    assert response.status_code == 403

    response = client.post(
        f"/api/tasks/?project_id={assigned_project.id}",
        json={"title": "Unauthorized task"},
        headers=headers
    )
    assert response.status_code == 403

    response = client.put(
        f"/api/tasks/{assigned_task.id}",
        json={"status": "completed"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

    response = client.put(
        f"/api/tasks/{assigned_task.id}",
        json={"title": "User cannot edit title"},
        headers=headers
    )
    assert response.status_code == 403

    response = client.put(
        f"/api/tasks/{assigned_task.id}",
        json={"status": "in_progress"},
        headers=headers
    )
    assert response.status_code == 403


def test_filter_tasks_by_status(client, db_session):
    headers = get_auth_headers(client, db_session)
    project_id = create_test_project(client, headers)

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


def test_update_task(client, db_session):
    headers = get_auth_headers(client, db_session)
    project_id = create_test_project(client, headers)

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


def test_delete_task(client, db_session):
    headers = get_auth_headers(client, db_session)
    project_id = create_test_project(client, headers)

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