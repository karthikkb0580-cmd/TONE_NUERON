from fastapi import APIRouter, Depends, Request

from backend.app.api.auth import get_current_user
from backend.app.core.rate_limit import limiter
from backend.app.models.user import User

from backend.app.schemas.ai import AIRequest, AIResponse
from backend.app.services.ai_service import process_ai_request


router = APIRouter(
    prefix="/api/v1/ai",
    tags=["Artificial Intelligence"],
)


FEATURES = {
    "analyze": "analyze",
    "tone": "tone",
    "sentiment": "sentiment",
    "emotion": "emotion",
    "rewrite": "rewrite",
    "grammar": "grammar",
    "translate": "translate",
    "suggest-reply": "suggest_reply",
    "summarize": "summarize",
    "expand": "expand",
    "coach": "coach",
    "toxicity": "toxicity",
}


def create_endpoint(feature):

    async def endpoint(
        request: Request,
        data: AIRequest,
        user: User = Depends(get_current_user),
    ):

        return await process_ai_request(
            user_id=user.id,
            feature=feature,
            data=data,
        )

    endpoint.__name__ = f"ai_{feature}"

    return limiter.shared_limit(
        "20/minute",
        scope="ai_inference",
    )(endpoint)


for path, feature in FEATURES.items():

    router.add_api_route(
        path=f"/{path}",
        endpoint=create_endpoint(feature),
        methods=["POST"],
        response_model=AIResponse,
        name=f"ai_{feature}",
        summary=feature.replace("_", " ").title(),
    )
