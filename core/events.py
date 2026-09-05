"""Small in-process event bus shared by the V0.2 runtime and UI."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable


EVENT_TYPES = (
    "CORE_STARTED", "AGENT_STARTED", "AGENT_STATE_CHANGED",
    "TASK_CREATED", "TASK_STARTED", "TASK_UPDATED", "TASK_COMPLETED",
    "TASK_FAILED", "TOOL_REQUESTED", "APPROVAL_REQUIRED",
    "APPROVAL_GRANTED", "APPROVAL_REJECTED", "VERIFICATION_STARTED",
    "VERIFICATION_COMPLETED", "VOICE_STATE_CHANGED",
)


@dataclass(frozen=True)
class CoreEvent:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class EventBus:
    """Thread-safe pub/sub with bounded history for dashboards and logs."""

    def __init__(self, history_limit: int = 100):
        self.history_limit = max(1, history_limit)
        self._history: list[CoreEvent] = []
        self._subscribers: list[Callable[[CoreEvent], None]] = []
        self._lock = RLock()

    def publish(self, event_type: str, **payload: Any) -> CoreEvent:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Unknown event type: {event_type}")
        event = CoreEvent(event_type, payload)
        with self._lock:
            self._history.append(event)
            del self._history[:-self.history_limit]
            subscribers = tuple(self._subscribers)
        for subscriber in subscribers:
            subscriber(event)
        return event

    def subscribe(self, callback: Callable[[CoreEvent], None]) -> Callable[[], None]:
        with self._lock:
            self._subscribers.append(callback)

        def unsubscribe() -> None:
            with self._lock:
                if callback in self._subscribers:
                    self._subscribers.remove(callback)

        return unsubscribe

    def recent(self, limit: int = 20) -> tuple[CoreEvent, ...]:
        with self._lock:
            return tuple(self._history[-max(1, limit):])
