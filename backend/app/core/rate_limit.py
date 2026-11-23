from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.core.config import settings


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri=settings.REDIS_URL,
)