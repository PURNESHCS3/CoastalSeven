from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.jwt import (
    get_current_user,
    require_admin,
)
from app.database import get_db
from app.models import User
from app.schemas import UserResponse


router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


# =========================
# Get Current User
# =========================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


# =========================
# Get All Users
# =========================

@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(User).all()


# =========================
# Admin-only: Get All Users
# =========================

@router.get(
    "/admin/all",
    response_model=list[UserResponse]
)
def get_all_users_admin(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return db.query(User).all()