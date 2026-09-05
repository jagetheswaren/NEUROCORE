"""Extensible registry of shared NEUROCORE agent capabilities."""

from dataclasses import dataclass
from typing import Type

from agents.base import AgentState, BaseAgent


@dataclass(frozen=True)
class AgentStatus:
    id: str
    name: str
    description: str
    capabilities: frozenset[str]
    state: AgentState
    configured: bool


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> BaseAgent:
        if not isinstance(agent, BaseAgent):
            raise TypeError("agent must inherit BaseAgent")
        if agent.id in self._agents:
            raise ValueError(f"Agent already registered: {agent.id}")
        self._agents[agent.id] = agent
        return agent

    def unregister(self, agent_id: str) -> BaseAgent:
        try:
            return self._agents.pop(agent_id)
        except KeyError as error:
            raise KeyError(f"Unknown agent: {agent_id}") from error

    def get(self, agent_id: str) -> BaseAgent:
        try:
            return self._agents[agent_id]
        except KeyError as error:
            raise KeyError(f"Unknown agent: {agent_id}") from error

    def list(self) -> tuple[BaseAgent, ...]:
        return tuple(self._agents.values())

    def by_capability(self, capability: str) -> tuple[BaseAgent, ...]:
        return tuple(
            agent for agent in self._agents.values()
            if capability in agent.capabilities
        )

    def statuses(self) -> tuple[AgentStatus, ...]:
        return tuple(
            AgentStatus(
                agent.id, agent.name, agent.description,
                agent.capabilities, agent.state,
                bool(agent.configuration.get("configured", True)),
            )
            for agent in self._agents.values()
        )

    @classmethod
    def defaults(cls, orchestrator=None) -> "AgentRegistry":
        registry = cls()
        registry.register(_GeneralAgent(orchestrator))
        registry.register(_ConfiguredAdapter("coding", "Coding", "Code generation and refactoring", {"filesystem.read", "testing"}, orchestrator))
        registry.register(_UnconfiguredAgent("research", "Research", "Web and document research", {"web.search", "knowledge.search"}))
        registry.register(_UnconfiguredAgent("project", "Project", "Project context and structure", {"filesystem.read"}))
        registry.register(_UnconfiguredAgent("knowledge", "Knowledge", "Knowledge retrieval", {"knowledge.search"}))
        registry.register(_UnconfiguredAgent("document", "Document", "Document extraction and summaries", {"document.read"}))
        registry.register(_UnconfiguredAgent("tools", "Tools", "Controlled tool execution", {"terminal.execute"}))
        registry.register(_UnconfiguredAgent("voice", "Voice", "Speech input and synthesis", {"speech_to_text", "text_to_speech"}))
        return registry


class _GeneralAgent(BaseAgent):
    id = "general"
    name = "General"
    description = "General conversation through the shared LLM boundary"
    capabilities = frozenset({"conversation"})

    def __init__(self, orchestrator=None):
        super().__init__(configuration={"configured": orchestrator is not None})
        self.orchestrator = orchestrator

    def execute(self, request: str, **kwargs):
        if self.orchestrator is None:
            raise RuntimeError("General agent is not configured")
        self.set_state(AgentState.THINKING)
        result = self.orchestrator.run(request, mode=kwargs.get("mode", "friend"))
        self.set_state(AgentState.COMPLETED)
        return result


class _ConfiguredAdapter(BaseAgent):
    def __init__(self, agent_id, name, description, capabilities, orchestrator):
        self.id = agent_id
        self.name = name
        self.description = description
        self.capabilities = frozenset(capabilities)
        super().__init__(configuration={"configured": orchestrator is not None})
        self.orchestrator = orchestrator

    def execute(self, request: str, **kwargs):
        if self.orchestrator is None:
            raise RuntimeError(f"{self.name} agent is not configured")
        self.set_state(AgentState.THINKING)
        result = self.orchestrator.run(request, mode="build")
        self.set_state(AgentState.COMPLETED)
        return result


class _UnconfiguredAgent(BaseAgent):
    def __init__(self, agent_id, name, description, capabilities):
        self.id = agent_id
        self.name = name
        self.description = description
        self.capabilities = frozenset(capabilities)
        super().__init__(configuration={"configured": False})

    def execute(self, request: str, **kwargs):
        raise RuntimeError(f"{self.name} agent is not configured")
