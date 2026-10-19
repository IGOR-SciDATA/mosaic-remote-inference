from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def live(request: Request):
    return {"status": "alive", "service": request.app.state.settings.service_name}


@router.get("/health/ready")
async def ready(request: Request):
    available = await request.app.state.inference_service.ready()
    return {"status": "ready" if available else "not_ready", "runtime_available": available}
