from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_role
from app.models.organization import Organization
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter()


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    organization = session.get(Organization, payload.organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    require_role(
        session=session,
        user_id=current_user.id,
        organization_id=payload.organization_id,
        allowed_roles={"owner", "admin"},
    )

    project = Project(**payload.model_dump())

    session.add(project)
    session.commit()
    session.refresh(project)

    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(
    organization_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    require_role(
        session=session,
        user_id=current_user.id,
        organization_id=organization_id,
        allowed_roles={"owner", "admin", "member", "viewer"},
    )

    projects = session.exec(
        select(Project).where(Project.organization_id == organization_id)
    ).all()

    return projects


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = session.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    require_role(
        session=session,
        user_id=current_user.id,
        organization_id=project.organization_id,
        allowed_roles={"owner", "admin"},
    )

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(project, key, value)

    session.add(project)
    session.commit()
    session.refresh(project)

    return project