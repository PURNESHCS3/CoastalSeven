from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.auth.jwt import require_admin
from app.crud import (
    get_admin_stats,
    get_task,
    update_task,
    update_user_role,
)
from app.database import get_db
from app.models import Task, User
from app.schemas import (
    AdminStatsResponse,
    TaskResponse,
    TaskUpdate,
    UserResponse,
    UserRoleUpdate,
    UserWithTasksResponse,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)


# ==========================================
# ADMIN STATS (Overview)
# ==========================================

@router.get(
    "/stats",
    response_model=AdminStatsResponse
)
def get_system_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return get_admin_stats(db)


# ==========================================
# GET ALL USERS AND THEIR TASKS
# ==========================================

@router.get(
    "/users-with-tasks",
    response_model=list[UserWithTasksResponse]
)
def list_users_and_tasks(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    users = db.query(User).all()
    return users


# ==========================================
# GIVE ADMIN ROLE TO ANOTHER USER
# ==========================================

@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse
)
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Optional safeguard: avoid demoting the last active admin if needed
    return update_user_role(db, user, role_data.role)


# ==========================================
# ADMIN EDIT ANY USER'S TASK
# ==========================================

@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def admin_update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if (
        task_data.status is not None
        and task_data.status not in {"pending", "in_progress", "completed"}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )

    if (
        task_data.priority is not None
        and task_data.priority not in {"low", "medium", "high"}
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid priority"
        )

    if task_data.assignee_id is not None:
        assignee = db.query(User).filter(User.id == task_data.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found"
            )

    return update_task(
        db=db,
        task=task,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        assignee_id=task_data.assignee_id
    )
