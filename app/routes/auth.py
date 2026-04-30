from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserOut
from app.core.rate_limit import (
    LOGIN_LIMIT,
    REGISTER_LIMIT,
    RedisRateLimiter,
    enforce_rate_limit,
)
from app.core.redis import get_redis
from app.core.audit import write_audit_log


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    limiter = RedisRateLimiter(get_redis())
    enforce_rate_limit(request, limiter, REGISTER_LIMIT)

    existing_user = session.exec(
        select(User).where(User.email == payload.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    background_tasks.add_task(
        write_audit_log,
        "register_success",
        str(user.id),
        user.email,
        f"ip={request.client.host if request.client else 'unknown'}",
    )

    return user


@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    background_tasks: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    limiter = RedisRateLimiter(get_redis())
    enforce_rate_limit(request, limiter, LOGIN_LIMIT)

    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        background_tasks.add_task(
            write_audit_log,
            "login_failed",
            "anonymous",
            form_data.username,
            f"ip={request.client.host if request.client else 'unknown'}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(str(user.id))

    background_tasks.add_task(
        write_audit_log,
        "login_success",
        str(user.id),
        user.email,
        f"ip={request.client.host if request.client else 'unknown'}",
    )

    return TokenResponse(access_token=access_token, token_type="bearer")