"""Non-blocking-ready task executor boundary for approved agent work."""

from core.events import EventBus
from core.tasks import Task, TaskStatus


class TaskExecutor:
    def __init__(self, registry, events: EventBus | None = None):
        self.registry = registry
        self.events = events or EventBus()
        self._cancelled: set[str] = set()

    def cancel(self, task_id: str) -> None:
        self._cancelled.add(task_id)

    def execute(self, task: Task) -> object:
        if task.id in self._cancelled:
            task.status = TaskStatus.CANCELLED
            return None
        task.status = TaskStatus.RUNNING
        self.events.publish("TASK_STARTED", task_id=task.id)
        if not task.current:
            task.status = TaskStatus.FAILED
            self.events.publish("TASK_FAILED", task_id=task.id, reason="No task steps")
            return None
        agent = self.registry.get(task.current.agent_id)
        self.events.publish("AGENT_STARTED", task_id=task.id, agent_id=agent.id)
        try:
            result = agent.execute(task.objective)
        except Exception as error:
            task.status = TaskStatus.FAILED
            task.current.status = TaskStatus.FAILED
            task.current.result = str(error)
            self.events.publish(
                "TASK_FAILED",
                task_id=task.id,
                agent_id=agent.id,
                reason=str(error),
            )
            raise
        task.current.result = str(result)
        task.current.status = TaskStatus.COMPLETED
        task.status = TaskStatus.COMPLETED
        self.events.publish("TASK_COMPLETED", task_id=task.id, agent_id=agent.id)
        return result
