import logging
from core.config import load_settings
from core.modes import ModeManager
from core.model import OllamaModel, OllamaModelError
from core.permissions import PermissionManager
from memory.database import MemoryDatabase
from memory.retrieval import retrieve
from knowledge.retrieval import KnowledgeRetriever
from tools.terminal import TerminalTool
from agents.registry import AgentRegistry
from core.events import EventBus
from core.executor import TaskExecutor
from core.planner import Planner
from core.verifier import Verifier


logger = logging.getLogger(__name__)


class Orchestrator:

    def __init__(self, settings=None):
        self.settings = (
            settings if settings is not None else load_settings()
        )

        self.modes = ModeManager()

        self.model = OllamaModel(
            model=self.settings.get("model", "qwen3:8b"),
            base_url=self.settings.get(
                "ollama_url",
                "http://127.0.0.1:11434"
            ),
            temperature=self.settings.get("temperature", 0.7),
            timeout=self.settings.get("ollama_timeout", 300)
        )

        self.memory = MemoryDatabase()
        self.knowledge = KnowledgeRetriever()
        self.permissions = PermissionManager(self.settings)
        self.terminal = TerminalTool(
            self.settings.get("workspace", "workspace"),
            timeout=self.settings.get("command_timeout", 120)
        )

        self.history = []
        self.events = EventBus()
        self.agent_registry = AgentRegistry.defaults(self)
        self.planner = Planner(self.events)
        self.executor = TaskExecutor(self.agent_registry, self.events)
        self.verifier = Verifier(self.events)
        self.events.publish("CORE_STARTED", model=self.settings.get("model", "qwen3:8b"))
        logger.info("Orchestrator initialized successfully")

    def create_task(self, objective, steps=None):
        """Create a shared task object without executing consequential work."""
        return self.planner.create_task(objective, steps)

    def execute_task(self, task):
        """Execute a planned task through the registered agent boundary."""
        result = self.executor.execute(task)
        return result, self.verifier.verify(task, result)

    def run(self, message, mode=None):
        try:
            mode_name = mode or self.modes.current
            mode_info = self.modes.get(mode_name)

            if mode_name == "terminal" and message.startswith("$"):
                return self._run_command(message[1:].strip())

            memories = retrieve(self.memory.get_all(), message)
            memory_context = ""
            if memories:
                memory_context = "\n".join(f"- {memory[1]}" for memory in memories)

            rag_context = self.knowledge.format_rag_context(message)

            system = mode_info.prompt
            if memory_context:
                system += "\n\nRelevant long-term memory:\n" + memory_context
            if rag_context:
                system += "\n\n" + rag_context

            self.history.append({
                "role": "user",
                "content": message
            })

            logger.debug(f"Running in {mode_name} mode with message: {message[:50]}...")
            
            answer = self.model.chat_messages(
                self.history[-10:],
                system
            )

            self.history.append({
                "role": "assistant",
                "content": answer
            })

            return answer
            
        except OllamaModelError as e:
            error_response = str(e)
            logger.error(f"OllamaModel error: {error_response}")
            self.history.append({
                "role": "assistant",
                "content": error_response
            })
            return error_response
            
        except Exception as e:
            error_response = f"⚠️ Unexpected error: {str(e)}"
            logger.exception("Unexpected error in orchestrator.run()")
            self.history.append({
                "role": "assistant",
                "content": error_response
            })
            return error_response

    def stream_response(self, message, mode=None):
        """Stream response tokens for real-time UI updates."""
        try:
            mode_name = mode or self.modes.current
            mode_info = self.modes.get(mode_name)

            if mode_name == "terminal" and message.startswith("$"):
                # Terminal mode - return full response at once
                yield self._run_command(message[1:].strip())
                return

            memories = retrieve(self.memory.get_all(), message)
            memory_context = ""
            if memories:
                memory_context = "\n".join(f"- {memory[1]}" for memory in memories)

            rag_context = self.knowledge.format_rag_context(message)

            system = mode_info.prompt
            if memory_context:
                system += "\n\nRelevant long-term memory:\n" + memory_context
            if rag_context:
                system += "\n\n" + rag_context

            # Add user message to history
            self.history.append({
                "role": "user",
                "content": message
            })

            logger.debug(f"Streaming in {mode_name} mode with message: {message[:50]}...")
            
            # Stream response tokens
            full_response = ""
            for token in self.model.stream_chat_messages(
                self.history[-10:],
                system
            ):
                full_response += token
                yield token
            
            # Save complete response to history
            self.history.append({
                "role": "assistant",
                "content": full_response
            })
            
        except OllamaModelError as e:
            error_response = str(e)
            logger.error(f"OllamaModel error: {error_response}")
            self.history.append({
                "role": "assistant",
                "content": error_response
            })
            yield error_response
            
        except Exception as e:
            error_response = f"⚠️ Unexpected error: {str(e)}"
            logger.exception("Unexpected error in orchestrator.stream_response()")
            self.history.append({
                "role": "assistant",
                "content": error_response
            })
            yield error_response

    def _run_command(self, command):
        if not command:
            return "Empty command."

        allowed, reason = self.permissions.request(command)

        if not allowed:
            return f"⛔ Command blocked ({reason}): {command}"

        code, output = self.terminal.run(command)

        if not output.strip():
            return f"[exit code {code} — no output]"

        return f"[exit code {code}]\n{output}"

    def remember(self, content):
        self.memory.save(content)
        return "Memory saved successfully."

    def list_memories(self):
        return self.memory.get_all()