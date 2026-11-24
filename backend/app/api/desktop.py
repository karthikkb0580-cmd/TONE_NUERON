from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.desktop import (
    DeviceRegister,
    DeviceUpdate,
    DeviceResponse,
)
from backend.app.services import desktop_service


router = APIRouter(
    prefix="/api/v1/desktop",
    tags=["Desktop Devices"],
)


@router.post(
    "/devices/register",
    response_model=DeviceResponse,
)
def register(
    data: DeviceRegister,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return desktop_service.register_device(
        db, user.id, data
    )


@router.get(
    "/devices",
    response_model=list[DeviceResponse],
)
def devices(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return desktop_service.list_devices(
        db, user.id, limit, offset
    )


@router.get(
    "/devices/{device_id}",
    response_model=DeviceResponse,
)
def get_device(
    device_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return desktop_service.get_device(
        db, user.id, device_id
    )


@router.patch(
    "/devices/{device_id}",
    response_model=DeviceResponse,
)
def update(
    device_id: UUID,
    data: DeviceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return desktop_service.update_device(
        db, user.id, device_id, data
    )


@router.post(
    "/devices/{device_id}/heartbeat",
    response_model=DeviceResponse,
)
def heartbeat(
    device_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return desktop_service.heartbeat(
        db, user.id, device_id
    )


@router.delete(
    "/devices/{device_id}",
    status_code=204,
)
def remove(
    device_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    desktop_service.delete_device(
        db, user.id, device_id
    )

    return Response(status_code=204)
