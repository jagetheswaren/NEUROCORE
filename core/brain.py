from core.orchestrator import Orchestrator


class NeuroCore:

    def __init__(self):
        self.orchestrator = Orchestrator()
        self.model = self.orchestrator.model
        self.memory = self.orchestrator.memory

    def ask(self, message: str) -> str:
        return self.orchestrator.run(message, mode="friend")

    def remember(self, content: str):
        return self.orchestrator.remember(content)