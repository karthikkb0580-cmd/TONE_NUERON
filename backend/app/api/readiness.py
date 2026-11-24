from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.app.services.readiness_service import check_readiness


router = APIRouter(tags=["System"])


@router.get("/ready")
async def readiness():

    result = await check_readiness()

    return JSONResponse(
        status_code=(
            200
            if result["status"] == "ready"
            else 503
        ),
        content=result,
        headers={"Cache-Control": "no-store"},
    )
