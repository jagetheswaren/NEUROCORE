import logging
from core.orchestrator import Orchestrator
from core.model_router import ModelRouter
from security.audit import AuditLogger

logger = logging.getLogger("server.dependencies")

_orchestrator_instance = None
_model_router_instance = None
_audit_logger_instance = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        logger.info("Initializing global Orchestrator instance for API Server")
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance

def get_model_router() -> ModelRouter:
    global _model_router_instance
    if _model_router_instance is None:
        logger.info("Initializing global ModelRouter instance for API Server")
        _model_router_instance = ModelRouter()
    return _model_router_instance

def get_audit_logger() -> AuditLogger:
    global _audit_logger_instance
    if _audit_logger_instance is None:
        _audit_logger_instance = AuditLogger()
    return _audit_logger_instance
