"""Explicit verification hook; never trusts an agent's success claim alone."""

from dataclasses import dataclass

from core.events import EventBus
from core.tasks import Task, TaskStatus


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    reason: str


class Verifier:
    def __init__(self, events: EventBus | None = None):
        self.events = events or EventBus()

    def verify(self, task: Task, result: object) -> VerificationResult:
        self.events.publish("VERIFICATION_STARTED", task_id=task.id)
        passed = result is not None and bool(str(result).strip())
        verification = VerificationResult(
            passed,
            "A bounded result was returned." if passed else "No result was returned.",
        )
        self.events.publish(
            "VERIFICATION_COMPLETED",
            task_id=task.id,
            passed=verification.passed,
        )
        return verification
