# ==========================================
# ADMIN ROUTE TESTS
# ==========================================
from app.models import User, Project, Task
from app.auth.jwt import create_access_token, hash_password


def get_admin_token(client, db_session):
    admin = User(
        username="superadmin_test",
        email="superadmin@example.com",
        hashed_password=hash_password("adminpass123"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = create_access_token(user_id=admin.id)
    return {"Authorization": f"Bearer {token}"}, admin


def get_user_token(client, db_session):
    user = User(
        username="test_peasant",
        email="peasant@example.com",
        hashed_password=hash_password("userpass123"),
        role="user",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user_id=user.id)
    return {"Authorization": f"Bearer {token}"}, user


def test_admin_stats(client, db_session):
    headers, _ = get_admin_token(client, db_session)
    response = client.get("/api/admin/stats", headers=headers)
    assert response.status_code == 200
    stats = response.json()
    assert "total_users" in stats
    assert "total_projects" in stats
    assert "total_tasks" in stats
    assert stats["total_users"] >= 1


def test_admin_stats_forbidden_for_regular_user(client, db_session):
    headers, _ = get_user_token(client, db_session)
    response = client.get("/api/admin/stats", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_users_with_tasks(client, db_session):
    headers, admin = get_admin_token(client, db_session)
    # Create project and task
    project = Project(name="Admin View Project", owner_id=admin.id)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    task = Task(title="Assigned Task", project_id=project.id, assignee_id=admin.id, priority="high")
    db_session.add(task)
    db_session.commit()

    response = client.get("/api/admin/users-with-tasks", headers=headers)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    admin_data = next((u for u in users if u["id"] == admin.id), None)
    assert admin_data is not None
    assert len(admin_data["assigned_tasks"]) >= 1


def test_admin_give_admin_role_to_another_user(client, db_session):
    admin_headers, _ = get_admin_token(client, db_session)
    _, user = get_user_token(client, db_session)

    assert user.role == "user"

    # Promote to admin
    response = client.put(
        f"/api/admin/users/{user.id}/role",
        json={"role": "admin"},
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"

    # Verify user is now admin in DB
    db_session.refresh(user)
    assert user.role == "admin"


def test_admin_edit_any_user_task(client, db_session):
    admin_headers, admin = get_admin_token(client, db_session)
    _, user = get_user_token(client, db_session)

    # Project owned by admin, task assigned to user
    project = Project(name="Task Editing Project", owner_id=admin.id)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    task = Task(title="User's Original Task", project_id=project.id, assignee_id=user.id, priority="low")
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    # Admin updates task
    response = client.put(
        f"/api/admin/tasks/{task.id}",
        json={
            "title": "Admin Overridden Task Title",
            "priority": "high",
            "status": "in_progress"
        },
        headers=admin_headers
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Admin Overridden Task Title"
    assert updated["priority"] == "high"
    assert updated["status"] == "in_progress"
