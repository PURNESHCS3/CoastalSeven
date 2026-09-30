from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user, require_admin
from app.crud import (
    assign_project_member,
    create_project,
    delete_project,
    get_project,
    get_projects,
    remove_project_member,
    update_project,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    ProjectAssign,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectWithMembersResponse,
    UserResponse,
)


router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)


# ==========================================
# CREATE PROJECT (Admin only)
# ==========================================

@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return create_project(
        db=db,
        name=project_data.name,
        description=project_data.description,
        owner_id=admin_user.id
    )


# ==========================================
# GET ALL PROJECTS (All authenticated users)
# ==========================================

@router.get(
    "/",
    response_model=list[ProjectResponse]
)
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_projects(db)


# ==========================================
# GET SINGLE PROJECT
# ==========================================

@router.get(
    "/{project_id}",
    response_model=ProjectWithMembersResponse
)
def get_single_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = get_project(db, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


# ==========================================
# UPDATE PROJECT (Admin or Owner)
# ==========================================

@router.put(
    "/{project_id}",
    response_model=ProjectResponse
)
def update_existing_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    project = get_project(db, project_id)



    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return update_project(
        db=db,
        project=project,
        name=project_data.name,
        description=project_data.description
    )

# ==========================================
# DELETE PROJECT (Admin only)
# ==========================================

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_project(
    project_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    project = get_project(db, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    delete_project(db, project)
    return None


# ==========================================
# ASSIGN PROJECT TO USER (Admin only)
# ==========================================

@router.post(
    "/{project_id}/assign",
    response_model=ProjectWithMembersResponse
)
def assign_user_to_project(
    project_id: int,
    assignment: ProjectAssign,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    user_to_assign = db.query(User).filter(User.id == assignment.user_id).first()
    if not user_to_assign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return assign_project_member(db, project, user_to_assign)


# ==========================================
# UNASSIGN USER FROM PROJECT (Admin only)
# ==========================================

@router.delete(
    "/{project_id}/assign/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def unassign_user_from_project(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    user_to_unassign = db.query(User).filter(User.id == user_id).first()
    if not user_to_unassign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    remove_project_member(db, project, user_to_unassign)
    return None


# ==========================================
# GET PROJECT MEMBERS
# ==========================================

@router.get(
    "/{project_id}/members",
    response_model=list[UserResponse]
)
def get_project_members_list(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    is_member = any(member.id == current_user.id for member in project.members)
    if (
        project.owner_id != current_user.id
        and not is_member
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return project.members