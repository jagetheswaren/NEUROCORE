"""Bounded planning abstraction that creates tasks but executes nothing."""

from core.events import EventBus
from core.tasks import Task, TaskStatus, TaskStep


class Planner:
    def __init__(self, events: EventBus | None = None):
        self.events = events or EventBus()

    def create_task(self, objective: str, steps: list[tuple[str, str]] | None = None) -> Task:
        if not objective.strip():
            raise ValueError("objective cannot be empty")
        task = Task(
            objective=objective,
            steps=[
                TaskStep(title=title, agent_id=agent_id)
                for title, agent_id in (steps or [("Understand request", "general")])
            ],
            status=TaskStatus.PLANNING,
        )
        self.events.publish("TASK_CREATED", task_id=task.id, objective=task.objective)
        return task
