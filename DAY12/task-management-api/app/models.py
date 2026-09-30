from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ==========================================
# ASSOCIATION TABLE: Project Members
# ==========================================

project_members = Table(
    "project_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner"
    )

    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="assignee"
    )

    assigned_projects: Mapped[list["Project"]] = relationship(
        "Project",
        secondary=project_members,
        back_populates="members"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="projects"
    )

    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    members: Mapped[list["User"]] = relationship(
        "User",
        secondary=project_members,
        back_populates="assigned_projects"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False
    )

    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks"
    )

    assignee: Mapped["User | None"] = relationship(
        "User",
        back_populates="assigned_tasks"
    )