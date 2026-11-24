from collections.abc import Awaitable, Callable

from app.schemas.inference import MLRequest, AIResponse


InferenceHandler = Callable[
    [MLRequest],
    Awaitable[AIResponse],
]


handlers: dict[str, InferenceHandler] = {}


def register_handler(
    feature: str,
    handler: InferenceHandler,
):

    handlers[feature] = handler


def get_handler(feature: str):

    return handlers.get(feature)


def available_features():

    return sorted(handlers.keys())
