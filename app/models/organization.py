from typing import TYPE_CHECKING, Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
import uuid

if TYPE_CHECKING:
    from app.models.membership import Membership
    from app.models.project import Project


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    memberships: List["Membership"] = Relationship(back_populates="organization")
    projects: List["Project"] = Relationship(back_populates="organization")