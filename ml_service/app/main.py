from fastapi import FastAPI

from app.api.inference import router as inference_router
from app.inference.registry import available_features


app = FastAPI(
    title="Tone Neuron ML Service",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


app.include_router(inference_router)


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "tone-neuron-ml",
        "models_ready": bool(available_features()),
        "available_features": available_features(),
    }
