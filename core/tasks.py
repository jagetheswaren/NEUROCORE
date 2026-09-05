"""Typed task objects used by planning, execution, verification, and UI."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import uuid4


class TaskStatus(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class TaskStep:
    title: str
    agent_id: str
    dependencies: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.CREATED
    result: Optional[str] = None


@dataclass
class Task:
    objective: str
    steps: list[TaskStep] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex[:12])
    current_step: int = 0
    status: TaskStatus = TaskStatus.CREATED

    @property
    def current(self) -> TaskStep | None:
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
