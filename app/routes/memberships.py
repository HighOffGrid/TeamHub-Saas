from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.models.membership import Membership
from app.schemas.membership import MembershipCreate, MembershipUpdateRole, MembershipOut
from app.services.membership_service import (
    create_membership,
    update_membership_role,
    delete_membership,
)
from app.models.membership import RoleEnum

router = APIRouter()


def get_actor_membership_or_403(
    organization_id: str,
    current_user: User,
    session: Session,
) -> Membership:
    membership = session.exec(
        select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == current_user.id,
        )
    ).first()

    if not membership or membership.role not in [RoleEnum.owner, RoleEnum.admin]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return membership


@router.get("/organizations/{organization_id}/memberships", response_model=list[MembershipOut])
def list_memberships(
    organization_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    actor_membership = session.exec(
        select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == current_user.id,
        )
    ).first()

    if not actor_membership:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="You do not belong to this organization")

    memberships = session.exec(
        select(Membership).where(Membership.organization_id == organization_id)
    ).all()

    return memberships


@router.post("/organizations/{organization_id}/memberships", response_model=MembershipOut, status_code=status.HTTP_201_CREATED)
def add_membership(
    organization_id: str,
    payload: MembershipCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    actor_membership = get_actor_membership_or_403(organization_id, current_user, session)
    return create_membership(
        session=session,
        organization_id=organization_id,
        user_email=payload.user_email,
        role=payload.role,
        actor_membership=actor_membership,
    )


@router.patch("/memberships/{membership_id}", response_model=MembershipOut)
def change_membership_role(
    membership_id: str,
    payload: MembershipUpdateRole,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    actor_membership = session.exec(
        select(Membership).where(Membership.user_id == current_user.id)
    ).first()

    if not actor_membership:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Membership not found for current user")

    return update_membership_role(
        session=session,
        membership_id=membership_id,
        new_role=payload.role,
        actor_membership=actor_membership,
    )


@router.delete("/memberships/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_membership(
    membership_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    target_membership = session.get(Membership, membership_id)
    if not target_membership:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Membership not found")

    actor_membership = session.exec(
        select(Membership).where(
            Membership.organization_id == target_membership.organization_id,
            Membership.user_id == current_user.id,
        )
    ).first()

    if not actor_membership or actor_membership.role not in [RoleEnum.owner, RoleEnum.admin]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    delete_membership(
        session=session,
        membership_id=membership_id,
        actor_membership=actor_membership,
    )