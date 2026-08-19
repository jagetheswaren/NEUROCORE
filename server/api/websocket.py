import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from server.api.dependencies import get_orchestrator, get_model_router

logger = logging.getLogger("server.websocket")
router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time streaming chat."""
    await websocket.accept()
    orchestrator = get_orchestrator()
    model_router = get_model_router()

    logger.info("WebSocket client connected")
    await websocket.send_json({
        "type": "system",
        "event": "connected",
        "message": "Connected to NEUROCORE Core Gateway - Streaming Ready"
    })

    try:
        while True:
            # Receive message from client
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
            except Exception as e:
                logger.warning(f"Failed to parse JSON: {e}")
                data = {"message": data_str, "mode": "friend"}

            msg = data.get("message", "").strip()
            mode = data.get("mode", "friend")

            if not msg:
                continue

            logger.debug(f"WebSocket request: mode={mode}, message_len={len(msg)}")

            # Get routing info
            route_info = model_router.route(msg, mode=mode)
            
            # Send status message
            await websocket.send_json({
                "type": "status",
                "event": "start_thinking",
                "mode": mode,
                "tier": route_info["tier"],
                "model": route_info["model"]
            })

            # Stream response tokens in real-time
            cumulative_response = ""
            token_count = 0
            
            try:
                for token in orchestrator.stream_response(msg, mode=mode):
                    cumulative_response += token
                    token_count += 1
                    
                    # Send token to client
                    await websocket.send_json({
                        "type": "message",
                        "event": "token",
                        "token": token,
                        "cumulative": cumulative_response,
                        "token_count": token_count
                    })
                
                # Send completion message
                await websocket.send_json({
                    "type": "message",
                    "event": "response_complete",
                    "content": cumulative_response,
                    "mode": mode,
                    "total_tokens": token_count
                })
                
                logger.debug(f"WebSocket response complete: {token_count} tokens")
                
            except Exception as stream_error:
                logger.error(f"Error during streaming: {stream_error}")
                await websocket.send_json({
                    "type": "error",
                    "event": "stream_error",
                    "message": str(stream_error)
                })

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "event": "connection_error",
                "message": str(e)
            })
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")
