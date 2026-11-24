from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.core.rate_limit import limiter
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.account import (
    AccountResponse,
    ChangePasswordRequest,
    DeleteAccountRequest,
)
from backend.app.services.account_service import (
    change_password,
    delete_account,
)


router = APIRouter(
    prefix="/api/v1/account",
    tags=["Account Management"],
)


@router.post(
    "/change-password",
    response_model=AccountResponse,
)
@limiter.limit("5/minute")
def change_account_password(
    request: Request,
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    change_password(
        db=db,
        user=user,
        current_password=data.current_password,
        new_password=data.new_password,
    )

    return AccountResponse(
        message="Password changed. Please log in again."
    )


@router.delete("", response_model=AccountResponse)
@limiter.limit("3/minute")
def remove_account(
    request: Request,
    data: DeleteAccountRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    delete_account(
        db=db,
        user=user,
        password=data.password,
        confirmation=data.confirmation,
    )

    return AccountResponse(
        message="Account deleted successfully."
    )
