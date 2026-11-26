from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import re
import uuid

from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from app.models.membership import Membership
    from app.models.project import Project


def generate_slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{slug}-{uuid.uuid4().hex[:8]}"


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    name: str
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    memberships: List["Membership"] = Relationship(
        back_populates="organization"
    )
    projects: List["Project"] = Relationship(
        back_populates="organization"
    )