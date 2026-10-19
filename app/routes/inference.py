from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.auth import require_bearer_token
from app.adapters.ollama import RuntimeUnavailable
from app.schemas import CapabilitiesResponse, InferenceRequest, InferenceResponse

router = APIRouter(tags=["inference"])


@router.get("/v1/capabilities", response_model=CapabilitiesResponse)
async def capabilities(request: Request):
    settings = request.app.state.settings
    return CapabilitiesResponse(service=settings.service_name, protocol_version="1", streaming=False, tools=False, configured_model=settings.runtime_model)


@router.post("/v1/inference", response_model=InferenceResponse, dependencies=[Depends(require_bearer_token)])
async def infer(body: InferenceRequest, request: Request):
    settings = request.app.state.settings
    try:
        output = await request.app.state.inference_service.infer(body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=str(exc)) from None
    except RuntimeUnavailable:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Inference runtime unavailable") from None
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Inference request failed") from None
    return InferenceResponse(model=settings.runtime_model, output_text=output)
