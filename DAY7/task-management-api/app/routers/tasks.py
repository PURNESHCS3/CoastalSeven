from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.crud import (
    create_task,
    delete_task,
    get_project,
    get_task,
    get_tasks,
    update_task,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)


router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"]
)


VALID_STATUSES = {
    "pending",
    "in_progress",
    "completed"
}

VALID_PRIORITIES = {
    "low",
    "medium",
    "high"
}


# ==========================================
# CREATE TASK
# ==========================================

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = get_project(
        db,
        project_id
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if (
        project.owner_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if task_data.priority not in VALID_PRIORITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid priority"
        )

    if task_data.assignee_id is not None:

        assignee = db.query(User).filter(
            User.id == task_data.assignee_id
        ).first()

        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found"
            )

    return create_task(
        db=db,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        project_id=project_id,
        assignee_id=task_data.assignee_id
    )


# ==========================================
# GET TASKS
# ==========================================

@router.get(
    "/",
    response_model=list[TaskResponse]
)
def list_tasks(
    project_id: int | None = None,

    status_filter: str | None = Query(
        default=None,
        alias="status"
    ),

    assignee_id: int | None = None,

    due_date: date | None = None,

    page: int = Query(
        default=1,
        ge=1
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    if status_filter is not None:

        if status_filter not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )

    skip = (page - 1) * limit

    return get_tasks(
        db=db,
        project_id=project_id,
        status=status_filter,
        assignee_id=assignee_id,
        due_date=due_date,
        skip=skip,
        limit=limit
    )


# ==========================================
# GET SINGLE TASK
# ==========================================

@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_single_task(
    task_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    task = get_task(
        db,
        task_id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    project = get_project(
        db,
        task.project_id
    )

    if (
        project.owner_id != current_user.id
        and task.assignee_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return task


# ==========================================
# UPDATE TASK
# ==========================================

@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_existing_task(
    task_id: int,

    task_data: TaskUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    task = get_task(
        db,
        task_id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    project = get_project(
        db,
        task.project_id
    )

    if (
        project.owner_id != current_user.id
        and task.assignee_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if (
        task_data.status is not None
        and task_data.status not in VALID_STATUSES
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )

    if (
        task_data.priority is not None
        and task_data.priority not in VALID_PRIORITIES
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid priority"
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


# ==========================================
# DELETE TASK
# ==========================================

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_task(
    task_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    task = get_task(
        db,
        task_id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    project = get_project(
        db,
        task.project_id
    )

    if (
        project.owner_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    delete_task(
        db,
        task
    )

    return None