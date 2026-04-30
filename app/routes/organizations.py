from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.models.organization import Organization
from app.models.membership import Membership
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationOut

router = APIRouter()


@router.post("/", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    org = Organization(**payload.model_dump())

    session.add(org)
    session.commit()
    session.refresh(org)

    membership = Membership(
        user_id=current_user.id,
        organization_id=org.id,
        role="admin",
    )

    session.add(membership)
    session.commit()

    return org


@router.get("/", response_model=list[OrganizationOut])
def list_my_organizations(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    memberships = session.exec(
        select(Membership).where(Membership.user_id == current_user.id)
    ).all()

    org_ids = [m.organization_id for m in memberships]

    if not org_ids:
        return []

    organizations = session.exec(
        select(Organization).where(Organization.id.in_(org_ids))
    ).all()

    return organizations