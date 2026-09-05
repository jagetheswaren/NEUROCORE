from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import logging
from server.api.dependencies import get_orchestrator, get_model_router

logger = logging.getLogger("server.routes.chat")

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "friend"
    tier: Optional[str] = None
    user_id: Optional[str] = "default_user"

class ChatResponse(BaseModel):
    response: str
    mode: str
    tier: str
    model: str
    history_length: int

@router.post("", response_model=ChatResponse)
def chat_endpoint(
    req: ChatRequest,
    orchestrator=Depends(get_orchestrator),
    model_router=Depends(get_model_router)
):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    # 1. Determine model tier
    route_info = model_router.route(req.message, mode=req.mode, requested_tier=req.tier)

    # 2. Run Orchestrator chat execution
    reply = orchestrator.run(req.message, mode=req.mode)

    return ChatResponse(
        response=reply,
        mode=req.mode,
        tier=route_info["tier"],
        model=route_info["model"],
        history_length=len(orchestrator.history)
    )

@router.post("/stream")
def chat_stream_endpoint(
    req: ChatRequest,
    orchestrator=Depends(get_orchestrator),
    model_router=Depends(get_model_router)
):
    """Stream chat response as Server-Sent Events (SSE)."""
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    route_info = model_router.route(req.message, mode=req.mode, requested_tier=req.tier)

    async def event_generator():
        """Generate SSE stream events."""
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'event': 'start', 'mode': req.mode, 'tier': route_info['tier']})}\n\n"
            
            # Stream tokens
            token_count = 0
            for token in orchestrator.stream_response(req.message, mode=req.mode):
                token_count += 1
                yield f"data: {json.dumps({'type': 'token', 'token': token, 'count': token_count})}\n\n"
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'total_tokens': token_count})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        headers={"content-type": "text/event-stream"}
    )

@router.get("/history")
def get_history(orchestrator=Depends(get_orchestrator)):
    return {
        "history": orchestrator.history,
        "count": len(orchestrator.history)
    }

@router.delete("/history")
def clear_history(orchestrator=Depends(get_orchestrator)):
    orchestrator.history = []
    return {"message": "Conversation history cleared successfully."}
