from agents.base import AgentState, BaseAgent
from agents.registry import AgentRegistry
from core.events import EventBus
from core.executor import TaskExecutor
from core.planner import Planner
from core.tasks import TaskStatus
from core.verifier import Verifier


class EchoAgent(BaseAgent):
    id = "echo"
    name = "Echo"
    capabilities = frozenset({"testing"})

    def execute(self, request, **kwargs):
        self.set_state(AgentState.COMPLETED)
        return request.upper()


def test_agent_state_and_cancellation():
    agent = EchoAgent()
    assert agent.state is AgentState.IDLE
    agent.set_state(AgentState.READY)
    assert agent.state is AgentState.READY
    agent.cancel()
    assert agent.state is AgentState.CANCELLED
    agent.reset()
    assert agent.state is AgentState.IDLE


def test_registry_lookup_and_capabilities():
    registry = AgentRegistry()
    agent = registry.register(EchoAgent())
    assert registry.get("echo") is agent
    assert registry.by_capability("testing") == (agent,)
    assert registry.statuses()[0].configured is True


def test_default_registry_reports_unconfigured_capabilities_truthfully():
    statuses = {status.id: status for status in AgentRegistry.defaults().statuses()}
    assert statuses["general"].configured is False
    assert statuses["voice"].configured is False
    assert statuses["voice"].state is AgentState.IDLE


def test_event_bus_history_and_unsubscribe():
    events = EventBus(history_limit=2)
    received = []
    unsubscribe = events.subscribe(received.append)
    events.publish("CORE_STARTED", source="test")
    events.publish("TASK_CREATED", task_id="one")
    events.publish("TASK_STARTED", task_id="one")
    unsubscribe()
    events.publish("TASK_COMPLETED", task_id="one")
    assert len(received) == 3
    assert [event.type for event in events.recent()] == ["TASK_STARTED", "TASK_COMPLETED"]


def test_planner_executor_and_verifier_share_one_task():
    events = EventBus()
    registry = AgentRegistry()
    registry.register(EchoAgent())
    planner = Planner(events)
    executor = TaskExecutor(registry, events)
    verifier = Verifier(events)

    task = planner.create_task("ship it", [("Run bounded check", "echo")])
    result = executor.execute(task)
    verification = verifier.verify(task, result)

    assert result == "SHIP IT"
    assert task.status is TaskStatus.COMPLETED
    assert verification.passed is True
    assert [event.type for event in events.recent()] == [
        "TASK_CREATED", "TASK_STARTED", "AGENT_STARTED",
        "TASK_COMPLETED", "VERIFICATION_STARTED", "VERIFICATION_COMPLETED",
    ]


def test_executor_marks_failed_agent_task():
    class BrokenAgent(EchoAgent):
        id = "broken"

        def execute(self, request, **kwargs):
            raise RuntimeError("provider unavailable")

    events = EventBus()
    registry = AgentRegistry()
    registry.register(BrokenAgent())
    task = Planner(events).create_task("fail safely", [("Run", "broken")])
    executor = TaskExecutor(registry, events)

    try:
        executor.execute(task)
    except RuntimeError:
        pass
    else:
        raise AssertionError("executor must surface agent failures")

    assert task.status is TaskStatus.FAILED
    assert events.recent()[-1].type == "TASK_FAILED"
