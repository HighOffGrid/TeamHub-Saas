from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from enum import Enum
import uuid

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.todo)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    project_id: str = Field(foreign_key="projects.id")
    assignee_id: Optional[str] = Field(default=None, foreign_key="users.id")
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    project: Optional["Project"] = Relationship(back_populates="tasks")
    assignee: Optional["User"] = Relationship(back_populates="tasks_assigned")