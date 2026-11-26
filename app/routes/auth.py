from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordBearer
from app.core.database import get_session
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
import uuid
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
from app.core.audit import dispatch_audit_log


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    request: Request,
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

    dispatch_audit_log(
        "register_success",
        str(user.id),
        user.email,
        f"ip={request.client.host if request.client else 'unknown'}",
    )

    return user


@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    limiter = RedisRateLimiter(get_redis())
    enforce_rate_limit(request, limiter, LOGIN_LIMIT)

    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        dispatch_audit_log(
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

    dispatch_audit_log(
        "login_success",
        str(user.id),
        user.email,
        f"ip={request.client.host if request.client else 'unknown'}",
    )

    return TokenResponse(access_token=access_token, token_type="bearer")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.get("/me", response_model=UserOut)
def read_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    user_id = decode_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    user = session.get(User, user_uuid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user