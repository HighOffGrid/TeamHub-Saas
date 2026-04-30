from pydantic  import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.project import ProjectStatus

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    organization_id: str

class ProjectOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: ProjectStatus
    organization_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None