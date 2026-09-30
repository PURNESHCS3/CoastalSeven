from datetime import date

from sqlalchemy.orm import Session

from app.models import Project, Task, User


# ==========================================
# PROJECT CRUD
# ==========================================

def create_project(
    db: Session,
    name: str,
    description: str | None,
    owner_id: int
):
    project = Project(
        name=name,
        description=description,
        owner_id=owner_id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_project(
    db: Session,
    project_id: int
):
    return (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )


def get_projects(
    db: Session,
    owner_id: int | None = None
):
    query = db.query(Project)

    if owner_id is not None:
        query = query.filter(
            Project.owner_id == owner_id
        )

    return query.all()


def update_project(
    db: Session,
    project: Project,
    name: str | None = None,
    description: str | None = None
):
    if name is not None:
        project.name = name

    if description is not None:
        project.description = description

    db.commit()
    db.refresh(project)

    return project


def delete_project(
    db: Session,
    project: Project
):
    db.delete(project)
    db.commit()


# ==========================================
# TASK CRUD
# ==========================================

def create_task(
    db: Session,
    title: str,
    description: str | None,
    priority: str,
    due_date: date | None,
    project_id: int,
    assignee_id: int | None
):
    task = Task(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        project_id=project_id,
        assignee_id=assignee_id,
        status="pending"
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_task(
    db: Session,
    task_id: int
):
    return (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )


def get_tasks(
    db: Session,
    project_id: int | None = None,
    status: str | None = None,
    assignee_id: int | None = None,
    due_date: date | None = None,
    skip: int = 0,
    limit: int = 10,
    current_user: User | None = None
):
    query = db.query(Task)

    if current_user is not None and current_user.role != "admin":
        query = query.filter(Task.assignee_id == current_user.id)

    if project_id is not None:
        query = query.filter(
            Task.project_id == project_id
        )

    if status is not None:
        query = query.filter(
            Task.status == status
        )

    if assignee_id is not None:
        query = query.filter(
            Task.assignee_id == assignee_id
        )

    if due_date is not None:
        query = query.filter(
            Task.due_date == due_date
        )

    return (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_task(
    db: Session,
    task: Task,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    due_date: date | None = None,
    assignee_id: int | None = None
):
    if title is not None:
        task.title = title

    if description is not None:
        task.description = description

    if status is not None:
        task.status = status

    if priority is not None:
        task.priority = priority

    if due_date is not None:
        task.due_date = due_date

    if assignee_id is not None:
        task.assignee_id = assignee_id

    db.commit()
    db.refresh(task)

    return task


def delete_task(
    db: Session,
    task: Task
):
    db.delete(task)
    db.commit()


# ==========================================
# ADMIN & MEMBERSHIP CRUD
# ==========================================

def assign_project_member(
    db: Session,
    project: Project,
    user: User
):
    if user not in project.members:
        project.members.append(user)
        db.commit()
        db.refresh(project)
    return project


def remove_project_member(
    db: Session,
    project: Project,
    user: User
):
    if user in project.members:
        project.members.remove(user)
        db.commit()
        db.refresh(project)
    return project


def update_user_role(
    db: Session,
    user: User,
    role: str
):
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def get_admin_stats(db: Session):
    total_users = db.query(User).count()
    total_projects = db.query(Project).count()
    total_tasks = db.query(Task).count()
    pending_tasks = db.query(Task).filter(Task.status == "pending").count()
    in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
    completed_tasks = db.query(Task).filter(Task.status == "completed").count()

    return {
        "total_users": total_users,
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
    }
