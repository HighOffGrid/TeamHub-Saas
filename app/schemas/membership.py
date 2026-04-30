from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from app.models.membership import RoleEnum

class MembershipCreate(BaseModel):
    user_email: EmailStr
    role: RoleEnum = RoleEnum.member

class MembershipUpdateRole(BaseModel):
    role: RoleEnum

class MembershipOut(BaseModel):
    id: str
    user_id: str
    organization_id: str
    role: RoleEnum
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)