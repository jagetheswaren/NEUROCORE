from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from server.api.dependencies import get_orchestrator, get_audit_logger

router = APIRouter(prefix="/tool", tags=["Tools"])

class ExecutionRequest(BaseModel):
    command: str
    mode: Optional[str] = "terminal"
    auto_approve_if_ask: Optional[bool] = False

class PermissionCheckRequest(BaseModel):
    command: str

@router.post("/execute")
def execute_tool_command(
    req: ExecutionRequest,
    orchestrator=Depends(get_orchestrator),
    audit_logger=Depends(get_audit_logger)
):
    if not req.command or not req.command.strip():
        raise HTTPException(status_code=400, detail="Command string cannot be empty.")

    st = orchestrator.permissions.status(req.command)

    if st == "blocked":
        audit_logger.log_action("api_user", req.mode, req.command, "blocked", False, "Blocked by security policy")
        raise HTTPException(status_code=403, detail=f"Command '{req.command}' is BLOCKED by security policy.")

    if st in {"sensitive", "ask"} and not req.auto_approve_if_ask:
        audit_logger.log_action("api_user", req.mode, req.command, st, False, "Pending approval")
        return {
            "status": "pending_approval",
            "risk_level": st,
            "command": req.command,
            "message": f"Command requires explicit client approval (Risk Level: {st.upper()})."
        }

    # Execute command safely
    success, output = orchestrator.execute_command(req.command)
    audit_logger.log_action("api_user", req.mode, req.command, st, True, output)

    return {
        "status": "executed",
        "command": req.command,
        "success": success,
        "output": output
    }

@router.post("/permission")
def check_permission(req: PermissionCheckRequest, orchestrator=Depends(get_orchestrator)):
    st = orchestrator.permissions.status(req.command)
    return {
        "command": req.command,
        "status": st,
        "allowed_without_prompt": st in {"auto", "safe"}
    }
