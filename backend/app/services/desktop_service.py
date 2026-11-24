from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.device import Device
from backend.app.models.user import User
from backend.app.schemas.desktop import (
    DeviceRegister,
    DeviceUpdate,
)


def get_device(
    db: Session,
    user_id: UUID,
    device_id: UUID,
):
    device = db.scalar(
        select(Device).where(
            Device.id == device_id,
            Device.user_id == user_id,
        )
    )

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found.",
        )

    return device


def register_device(
    db: Session,
    user_id: UUID,
    data: DeviceRegister,
):
    try:
        db.execute(
            select(User.id)
            .where(User.id == user_id)
            .with_for_update()
        )

        device = db.scalar(
            select(Device).where(
                Device.user_id == user_id,
                Device.installation_id == data.installation_id,
            )
        )

        if device is None:
            device = Device(
                user_id=user_id,
                **data.model_dump(),
            )

            db.add(device)

        else:
            device.device_name = data.device_name
            device.operating_system = data.operating_system
            device.app_version = data.app_version

        device.last_active_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(device)

        return device

    except Exception:
        db.rollback()
        raise


def list_devices(
    db: Session,
    user_id: UUID,
    limit: int,
    offset: int,
):
    return db.scalars(
        select(Device)
        .where(Device.user_id == user_id)
        .order_by(
            Device.last_active_at.desc(),
            Device.id.desc(),
        )
        .offset(offset)
        .limit(limit)
    ).all()


def update_device(
    db: Session,
    user_id: UUID,
    device_id: UUID,
    data: DeviceUpdate,
):
    device = get_device(db, user_id, device_id)

    for field, value in data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    ).items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)

    return device


def heartbeat(
    db: Session,
    user_id: UUID,
    device_id: UUID,
):
    device = get_device(db, user_id, device_id)

    device.last_active_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(device)

    return device


def delete_device(
    db: Session,
    user_id: UUID,
    device_id: UUID,
):
    device = get_device(db, user_id, device_id)

    db.delete(device)
    db.commit()
