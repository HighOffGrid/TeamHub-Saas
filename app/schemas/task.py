from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime, timezone
from app.models.task import TaskStatus, TaskPriority


def _ensure_utc(v: Optional[datetime]) -> Optional[datetime]:
    if v is not None and v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    return v


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: str
    assignee_id: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None

    @field_validator("due_date", mode="after")
    @classmethod
    def ensure_timezone(cls, v):
        return _ensure_utc(v)


class TaskOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    project_id: str
    assignee_id: Optional[str] = None
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None

    @field_validator("due_date", mode="after")
    @classmethod
    def ensure_timezone(cls, v):
        return _ensure_utc(v)