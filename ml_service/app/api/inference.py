from fastapi import APIRouter, Depends, HTTPException

from app.core.security import verify_internal_api_key
from app.schemas.inference import MLRequest, AIResponse
from app.inference.registry import (
    get_handler,
    available_features,
)


router = APIRouter(
    prefix="/internal/v1",
    dependencies=[Depends(verify_internal_api_key)],
)


@router.post(
    "/inference",
    response_model=AIResponse,
)
async def inference(data: MLRequest):

    handler = get_handler(data.feature)

    if handler is None:

        raise HTTPException(
            status_code=501,
            detail="Requested model is not implemented yet.",
        )

    return await handler(data)


@router.get("/capabilities")
def capabilities():

    return {
        "available_features": available_features(),
    }
