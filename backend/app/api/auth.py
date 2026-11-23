from datetime import datetime, timezone
from uuid import UUID

import jwt

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.rate_limit import limiter

from backend.app.database.session import get_db

from backend.app.models.user import User
from backend.app.models.refresh_token import RefreshToken

from backend.app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    UserResponse,
)

from backend.app.schemas.session import TokenPairResponse

from backend.app.services.auth_service import (
    register_user,
    authenticate_user,
)

from backend.app.services.session_service import create_session

from backend.app.services.login_security_service import (
    check_login_allowed,
    record_failed_login,
    clear_failed_logins,
)
from backend.app.services.security_event_service import (
    log_security_event,
    SecurityEventType,
)
from sqlalchemy import func, select


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

bearer_scheme = HTTPBearer()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
)
@limiter.limit("3/minute")
def register(
    request: Request,
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    user = register_user(db, data)

    return RegisterResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_verified=user.is_verified,
        message=(
            "Registration successful. "
            "Check your email for the verification code."
        ),
    )


@router.post(
    "/login",
    response_model=TokenPairResponse,
)
@limiter.limit("5/minute")
def login(
    request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()
    ip_address = request.client.host if request.client else None

    try:
        check_login_allowed(email)

    except HTTPException as exc:
        if exc.status_code == 429:
            user = db.scalar(
                select(User).where(func.lower(User.email) == email)
            )

            log_security_event(
                db=db,
                event_type=SecurityEventType.ACCOUNT_BLOCKED,
                user_id=user.id if user else None,
                ip_address=ip_address,
                details="Account-level login protection triggered",
            )

            db.commit()

        raise

    try:
        user = authenticate_user(
            db,
            email,
            data.password,
        )

    except HTTPException as exc:
        if exc.status_code == 401:
            record_failed_login(email)

            user = db.scalar(
                select(User).where(func.lower(User.email) == email)
            )

            log_security_event(
                db=db,
                event_type=SecurityEventType.LOGIN_FAILED,
                user_id=user.id if user else None,
                ip_address=ip_address,
                details="Invalid login credentials",
            )

            db.commit()

        raise

    # Create a valid authentication session.
    tokens = create_session(db, user.id)

    # Record successful authentication.
    log_security_event(
        db=db,
        event_type=SecurityEventType.LOGIN_SUCCESS,
        user_id=user.id,
        ip_address=ip_address,
        details="User authenticated successfully",
    )

    db.commit()

    # Clear previous failed attempts only after successful login.
    clear_failed_logins(email)

    return tokens


def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> RefreshToken:

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("type") != "access":
            raise ValueError("Invalid token type")

        user_id = UUID(payload["sub"])
        session_id = UUID(payload["sid"])

    except (
        jwt.InvalidTokenError,
        KeyError,
        ValueError,
        TypeError,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token.",
        )

    session = db.get(
        RefreshToken,
        session_id,
    )

    if (
        session is None
        or session.is_revoked
        or session.user_id != user_id
        or session.expires_at <= datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=401,
            detail="Session expired or revoked.",
        )

    return session


def get_current_user(
    session: RefreshToken = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> User:

    user = db.get(
        User,
        session.user_id,
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email verification required.",
        )

    return user

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user