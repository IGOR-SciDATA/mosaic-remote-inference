from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import Settings
from app.services.inference_service import InferenceService
from app.routes.health import router as health_router
from app.routes.inference import router as inference_router


def create_app(settings: Settings | None = None, inference_service: InferenceService | None = None) -> FastAPI:
    app = FastAPI(title="Mosaic Remote Inference", version="0.1.0", docs_url=None, redoc_url=None)
    app.state.settings = settings or Settings.from_env()
    app.state.inference_service = inference_service or InferenceService(app.state.settings)
    app.include_router(health_router)
    app.include_router(inference_router)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request, exc):
        # Pydantic errors can echo submitted values; expose only field locations and messages.
        safe_errors = [{"loc": error.get("loc", []), "msg": error.get("msg", "Invalid input"), "type": error.get("type", "value_error")} for error in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": safe_errors})

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request, exc):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


app = create_app()
