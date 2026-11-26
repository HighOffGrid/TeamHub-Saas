from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationOut(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)