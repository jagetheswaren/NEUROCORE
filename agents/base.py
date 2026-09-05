"""Common agent contract; agents expose status, not hidden reasoning."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class AgentState(str, Enum):
    IDLE = "IDLE"
    READY = "READY"
    THINKING = "THINKING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class BaseAgent(ABC):
    id = "agent"
    name = "Agent"
    description = ""
    capabilities: frozenset[str] = frozenset()

    def __init__(self, context=None, configuration=None):
        self.context = context
        self.configuration = configuration or {}
        self.state = AgentState.IDLE
        self._cancelled = False

    def set_state(self, state: AgentState) -> AgentState:
        self.state = state
        return state

    @abstractmethod
    def execute(self, request: str, **kwargs: Any) -> Any:
        """Execute one bounded request and return a user-safe result."""

    def cancel(self) -> None:
        self._cancelled = True
        self.state = AgentState.CANCELLED

    def reset(self) -> None:
        self._cancelled = False
        self.state = AgentState.IDLE
