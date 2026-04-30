from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.membership import Membership


def get_membership(session: Session, user_id: str, organization_id: str):
    membership = session.exec(
        select(Membership).where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id,
        )
    ).first()

    return membership


def require_role(
    session: Session,
    user_id: str,
    organization_id: str,
    allowed_roles: set[str],
):
    membership = get_membership(session, user_id, organization_id)

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this action",
        )

    return membership