from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SessionResponse(BaseModel):
    id: UUID
    created_at: datetime
    expires_at: datetime
    is_revoked: bool


class MessageResponse(BaseModel):
    message: str