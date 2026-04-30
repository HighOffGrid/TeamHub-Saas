from pydantic import BaseModel, ConfigDict
from typing import Optional 
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: str
    assignee_id: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None

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