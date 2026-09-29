from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password
)

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User

from app.schemas import (
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserLogin,
    UserResponse
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(
            user_data.password
        ),
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=Token
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(
            User.email == credentials.email
        )
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if not verify_password(
        credentials.password,
        user.hashed_password
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    access_token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": str(user.id)
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post(
    "/refresh",
    response_model=Token
)
def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):

    payload = decode_token(
        token_data.refresh_token
    )

    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    if payload.get("type") != "refresh":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )

    user_id = payload.get("sub")

    if user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    try:

        user_id = int(user_id)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    new_access_token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    return {
        "access_token": new_access_token,
        "refresh_token": token_data.refresh_token,
        "token_type": "bearer"
    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user