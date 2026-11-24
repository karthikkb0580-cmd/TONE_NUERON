from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeviceRegister(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    installation_id: UUID

    device_name: str = Field(
        min_length=1,
        max_length=100,
    )

    operating_system: Literal[
        "windows",
        "macos",
        "linux",
    ]

    app_version: str = Field(
        min_length=1,
        max_length=30,
    )


class DeviceUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    device_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    app_version: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    mascot_enabled: bool | None = None
    clipboard_enabled: bool | None = None
    selected_text_enabled: bool | None = None


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    installation_id: UUID
    device_name: str
    operating_system: str
    app_version: str
    mascot_enabled: bool
    clipboard_enabled: bool
    selected_text_enabled: bool
    created_at: datetime
    last_active_at: datetime
