from typing import TYPE_CHECKING, Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from enum import Enum
import uuid

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.task import Task


class ProjectStatus(str, Enum):
    active = "active"
    archived = "archived"


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    status: ProjectStatus = Field(default=ProjectStatus.active)
    organization_id: str = Field(foreign_key="organizations.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    organization: Optional["Organization"] = Relationship(back_populates="projects")
    tasks: List["Task"] = Relationship(back_populates="project")