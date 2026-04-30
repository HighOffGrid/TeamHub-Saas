from typing import TYPE_CHECKING, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
import uuid

if TYPE_CHECKING:
    from app.models.membership import Membership
    from app.models.task import Task


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    memberships: List["Membership"] = Relationship(back_populates="user")
    tasks_assigned: List["Task"] = Relationship(back_populates="assignee")