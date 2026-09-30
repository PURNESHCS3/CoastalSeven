from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==========================================
# USER SCHEMAS
# ==========================================

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================
# AUTHENTICATION SCHEMAS
# ==========================================

class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


# ==========================================
# PROJECT SCHEMAS
# ==========================================

class ProjectCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )

    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    description: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================
# TASK SCHEMAS
# ==========================================

class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200
    )

    description: str | None = None

    priority: str = "medium"

    due_date: date | None = None

    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: str | None = None

    status: str | None = None

    priority: str | None = None

    due_date: date | None = None

    assignee_id: int | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: str
    due_date: date | None
    project_id: int
    assignee_id: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )