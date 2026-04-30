from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import decode_token
from app.models.user import User
from app.models.membership import Membership, RoleEnum
from app.models.organization import Organization

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    user_id = decode_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_organization_or_404(
    organization_id: str,
    session: Session = Depends(get_session),
) -> Organization:
    organization = session.get(Organization, organization_id)

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return organization


def get_current_membership(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Membership:
    membership = session.exec(
        select(Membership)
        .where(Membership.user_id == current_user.id)
        .where(Membership.organization_id == organization_id)
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    return membership


def require_org_role(*allowed_roles: RoleEnum):
    def checker(
        membership: Membership = Depends(get_current_membership),
    ) -> Membership:
        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return membership

    return checker


def require_org_member(
    membership: Membership = Depends(get_current_membership),
) -> Membership:
    return membership


def require_org_manager(
    membership: Membership = Depends(get_current_membership),
) -> Membership:
    if membership.role not in [RoleEnum.owner, RoleEnum.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization managers can perform this action",
        )
    return membership


def require_org_owner(
    membership: Membership = Depends(get_current_membership),
) -> Membership:
    if membership.role != RoleEnum.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owners can perform this action",
        )
    return membership