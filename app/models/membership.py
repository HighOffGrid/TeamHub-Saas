from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from datetime import datetime, timezone
from enum import Enum
import uuid

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class RoleEnum(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    viewer = "viewer"


class Membership(SQLModel, table=True):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_membership_user_organization"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    organization_id: str = Field(foreign_key="organizations.id", index=True)
    role: RoleEnum = Field(default=RoleEnum.member)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional["User"] = Relationship(back_populates="memberships")
    organization: Optional["Organization"] = Relationship(back_populates="memberships")