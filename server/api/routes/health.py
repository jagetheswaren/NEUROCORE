from fastapi import APIRouter, Depends
from server.api.dependencies import get_orchestrator

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(orchestrator=Depends(get_orchestrator)):
    ollama_ok = False
    try:
        ollama_ok = orchestrator.model.health_check()
    except Exception:
        ollama_ok = False

    return {
        "status": "online",
        "version": "0.5.0",
        "services": {
            "api_gateway": "healthy",
            "ollama_runtime": "connected" if ollama_ok else "disconnected",
            "memory_database": "ready"
        }
    }

@router.get("/health/ollama")
def ollama_health(orchestrator=Depends(get_orchestrator)):
    is_up = orchestrator.model.health_check()
    return {
        "ollama_url": orchestrator.model.base_url,
        "model": orchestrator.model.model,
        "status": "connected" if is_up else "unreachable"
    }
