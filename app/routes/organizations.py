from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.membership import Membership, RoleEnum
from app.core.database import get_session
from app.dependencies.auth import get_current_user
from app.models.organization import Organization, generate_slug
from app.models.membership import Membership
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationOut,
    OrganizationUpdate,
)

router = APIRouter()


@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    org = Organization(
        name=payload.name,
        slug=generate_slug(payload.name),
        description=payload.description,
    )
    session.add(org)
    session.flush()

    membership = Membership(
        user_id=current_user.id,
        organization_id=org.id,
        role=RoleEnum.owner,
    )
    session.add(membership)
    session.commit()
    session.refresh(org)

    return org

@router.get("", response_model=list[OrganizationOut])
def list_my_organizations(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    memberships = session.exec(
        select(Membership).where(Membership.user_id == current_user.id)
    ).all()

    org_ids = [membership.organization_id for membership in memberships]

    if not org_ids:
        return []

    organizations = session.exec(
        select(Organization).where(Organization.id.in_(org_ids))
    ).all()

    return organizations


@router.get("/{organization_id}", response_model=OrganizationOut)
def get_organization(
    organization_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == organization_id,
        )
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    organization = session.get(Organization, organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization

@router.patch("/{organization_id}", response_model=OrganizationOut)
def update_organization(
    organization_id: str,
    payload: OrganizationUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == organization_id,
        )
    ).first()

    if not membership or membership.role not in [RoleEnum.owner, RoleEnum.admin]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    organization = session.get(Organization, organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if payload.name is not None:
        organization.name = payload.name

    if payload.description is not None:
        organization.description = payload.description

    session.add(organization)
    session.commit()
    session.refresh(organization)

    return organization

@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
    organization_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == current_user.id,
            Membership.organization_id == organization_id,
        )
    ).first()

    if not membership or membership.role != RoleEnum.owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    organization = session.get(Organization, organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    memberships = session.exec(
        select(Membership).where(
            Membership.organization_id == organization_id
        )
    ).all()

    for membership_item in memberships:
        session.delete(membership_item)

    session.delete(organization)
    session.commit()