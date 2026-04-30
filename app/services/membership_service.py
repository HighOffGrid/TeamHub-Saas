from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.membership import Membership, RoleEnum
from app.models.organization import Organization
from app.models.user import User


def get_organization_or_404(session: Session, organization_id: str) -> Organization:
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


def get_user_by_email_or_404(session: Session, email: str) -> User:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_membership_by_id_or_404(session: Session, membership_id: str) -> Membership:
    membership = session.get(Membership, membership_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership


def create_membership(
    session: Session,
    organization_id: str,
    user_email: str,
    role: RoleEnum,
    actor_membership: Membership,
) -> Membership:
    get_organization_or_404(session, organization_id)
    user = get_user_by_email_or_404(session, user_email)

    existing = session.exec(
        select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == user.id,
        )
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="User is already a member of this organization")

    if actor_membership.role == RoleEnum.admin and role in [RoleEnum.admin, RoleEnum.owner]:
        raise HTTPException(
            status_code=403,
            detail="Admins cannot create admins or owners",
        )

    membership = Membership(
        organization_id=organization_id,
        user_id=user.id,
        role=role,
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def update_membership_role(
    session: Session,
    membership_id: str,
    new_role: RoleEnum,
    actor_membership: Membership,
) -> Membership:
    membership = get_membership_by_id_or_404(session, membership_id)

    if actor_membership.organization_id != membership.organization_id:
        raise HTTPException(status_code=403, detail="Cannot manage members from another organization")

    if actor_membership.role == RoleEnum.admin and new_role in [RoleEnum.admin, RoleEnum.owner]:
        raise HTTPException(
            status_code=403,
            detail="Admins cannot promote users to admin or owner",
        )

    if membership.role == RoleEnum.owner and new_role != RoleEnum.owner:
        owners = session.exec(
            select(Membership).where(
                Membership.organization_id == membership.organization_id,
                Membership.role == RoleEnum.owner,
            )
        ).all()

        if len(owners) == 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot demote the last owner of the organization",
            )

    membership.role = new_role
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership


def delete_membership(
    session: Session,
    membership_id: str,
    actor_membership: Membership,
) -> None:
    membership = get_membership_by_id_or_404(session, membership_id)

    if actor_membership.organization_id != membership.organization_id:
        raise HTTPException(status_code=403, detail="Cannot remove members from another organization")

    if membership.role == RoleEnum.owner:
        owners = session.exec(
            select(Membership).where(
                Membership.organization_id == membership.organization_id,
                Membership.role == RoleEnum.owner,
            )
        ).all()

        if len(owners) == 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last owner of the organization",
            )

    if actor_membership.role == RoleEnum.admin and membership.role in [RoleEnum.admin, RoleEnum.owner]:
        raise HTTPException(
            status_code=403,
            detail="Admins cannot remove admins or owners",
        )

    session.delete(membership)
    session.commit()