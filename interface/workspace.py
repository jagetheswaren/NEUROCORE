"""Opt-in V0.2 Command Deck workspace for the Textual terminal UI."""

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, RichLog, Static

from interface.design import WORKSPACE_CSS
from interface.registry import SCREENS, get_screen
from interface.sounds import SoundEngine
from agents.registry import AgentRegistry


class CommandDeckTUI(App):
    """A responsive workspace shell that presents safe, user-visible state."""

    CSS = WORKSPACE_CSS
    BINDINGS = [
        ("ctrl+c", "quit", "Exit"),
        ("ctrl+l", "redraw", "Redraw"),
        ("ctrl+1", "show_dashboard", "Dashboard"),
        ("ctrl+2", "show_chat", "Chat"),
        ("ctrl+3", "show_agents", "Agents"),
        ("ctrl+4", "show_tasks", "Tasks"),
        ("ctrl+5", "show_voice", "Voice"),
    ]

    def __init__(self, orchestrator, settings, **kwargs):
        super().__init__(**kwargs)
        self.orchestrator = orchestrator
        self.settings = settings
        self.online = False
        self.active_key = "dashboard"
        self.sound = SoundEngine(
            settings.get("sound_enabled", False),
            settings.get("sound_volume", 0.2),
        )
        self.agent_registry = getattr(
            orchestrator, "agent_registry", AgentRegistry.defaults(orchestrator)
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="deck"):
            with Vertical(id="rail"):
                yield Static("NEUROCORE", id="rail-title")
                yield Static("// COMMAND DECK", id="rail-subtitle")
                for screen in SCREENS:
                    yield Button(
                        f"{screen.shortcut}  {screen.title}",
                        id=f"nav-{screen.key}",
                    )
                yield Static("\nV0.2 WORKSPACE\nOPT-IN", classes="muted")
            with Vertical(id="workspace"):
                with Vertical(id="context"):
                    yield Static(id="context-title")
                    yield Static(id="context-meta")
                with Vertical(id="canvas"):
                    yield Static(id="canvas-title")
                    yield Static(id="canvas-body")
                    yield RichLog(id="run-log", markup=True, wrap=True)
                yield Input(
                    placeholder="Command Deck input · ask, plan, or navigate",
                    id="command",
                )
            with Vertical(id="inspector"):
                yield Static("ACTIVITY / INSPECTOR", id="inspector-title")
                yield Static(id="inspector-body")
        yield Footer()

    def on_mount(self) -> None:
        self._render_screen()
        self.query_one("#command", Input).focus()
        self.check_connection()

    def on_resize(self, event) -> None:
        narrow = event.size.width < 96
        very_narrow = event.size.width < 70
        self.query_one("#rail").display = not very_narrow
        self.query_one("#inspector").display = not narrow

    @on(Button.Pressed)
    def navigate(self, event: Button.Pressed) -> None:
        key = event.button.id.removeprefix("nav-")
        self.show_screen(key)

    @on(Input.Submitted, "#command")
    def submit(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        event.input.value = ""
        if not text:
            return
        if text.lower() in {"exit", "quit"}:
            self.exit()
            return
        if text.startswith(":"):
            key = text[1:].lower()
            if any(screen.key == key for screen in SCREENS):
                self.show_screen(key)
                return
        self.show_screen("chat")
        self._write(f"[bold green]YOU[/]  {text}")
        self.stream_response(text)

    def show_screen(self, key: str) -> None:
        get_screen(key)
        self.active_key = key
        self._render_screen()

    def _render_screen(self) -> None:
        screen = get_screen(self.active_key)
        self.query_one("#context-title", Static).update(
            f"NEUROCORE / {screen.title.upper()}"
        )
        self.query_one("#context-meta", Static).update(
            f"RUN ACTIVE  ·  MODEL {self.settings.get('model', 'qwen3:8b')}  ·  "
            f"OLLAMA {'ONLINE' if self.online else 'CHECKING'}"
        )
        self.query_one("#canvas-title", Static).update(
            f"{screen.title.upper()}  //  {screen.description}"
        )
        self.query_one("#canvas-body", Static).update(self._screen_body())
        self.query_one("#inspector-body", Static).update(
            "[bold]STATE[/]\n"
            "IDLE\n\n"
            "[bold]MODEL[/]\n"
            f"{self.settings.get('model', 'qwen3:8b')}\n\n"
            "[bold]SAFETY[/]\n"
            "Approval-controlled\n\n"
            "[bold]SOUND[/]\n"
            f"{'ON' if self.sound.enabled else 'OFF'}"
        )
        for item in SCREENS:
            button = self.query_one(f"#nav-{item.key}", Button)
            button.remove_class("-active")
            if item.key == self.active_key:
                button.add_class("-active")

    def _screen_body(self) -> str:
        if self.active_key == "agents":
            lines = ["[bold]REGISTERED AGENTS[/]", ""]
            for status in self.agent_registry.statuses():
                marker = "●" if status.configured else "○"
                state = status.state.value if status.configured else "NOT CONFIGURED"
                lines.append(f"{marker} {status.name:<10} {state}")
            lines.extend(["", "[approval]Capabilities do not grant tool permissions.[/]"])
            return "\n".join(lines)
        bodies = {
            "dashboard": (
                "[bold]SYSTEM READY[/]\n\n"
                "A controlled local AI workspace.\n"
                "Use the rail or Ctrl+1..5 to move between surfaces.\n\n"
                "[state]● V0.1 FOUNDATION STABLE[/]\n"
                "[muted]V0.2 workspace is additive and opt-in.[/]"
            ),
            "chat": "Conversation stream is ready.\n\nAsk NEUROCORE anything.",
            "tasks": (
                "[bold]TASK PIPELINE[/]\n\n"
                "IDLE → ROUTING → PLANNING → APPROVAL → EXECUTION → VERIFIED\n\n"
                "[muted]No active task. New runs will appear in the activity log.[/]"
            ),
            "voice": (
                "[bold]VOICE CAPABILITY[/]\n\n"
                "Status: optional / lazy-loaded\n"
                "Speech input and synthesis remain disabled until configured.\n\n"
                "[muted]No microphone or audio model is required for text mode.[/]"
            ),
            "projects": "[bold]PROJECTS[/]\n\nNo project selected.",
            "memory": "[bold]MEMORY[/]\n\nPersistent context is available through the core.",
            "settings": "[bold]SETTINGS[/]\n\nUse the V0.1 settings modal for runtime preferences.",
        }
        return bodies[self.active_key]

    @work(exclusive=True, thread=True)
    def check_connection(self) -> None:
        self.online = self.orchestrator.model.health_check()
        self.call_from_thread(self._render_screen)

    @work(thread=True, exclusive=True)
    def stream_response(self, text: str) -> None:
        self.call_from_thread(self._write, "[magenta]ROUTING  ●  STREAMING[/]")
        response = ""
        try:
            for token in self.orchestrator.stream_response(text):
                response += token
                self.call_from_thread(self._write, f"[magenta]NEUROCORE[/]  {response}")
            self.call_from_thread(self._write, "[green]VERIFIED  ●  RESPONSE COMPLETE[/]")
        except Exception as error:
            self.call_from_thread(self._write, f"[red]FAILED  ●  {error}[/]")

    def _write(self, content: str) -> None:
        self.query_one("#run-log", RichLog).write(content)

    def action_redraw(self) -> None:
        self.refresh(layout=True)

    def action_show_dashboard(self) -> None:
        self.show_screen("dashboard")

    def action_show_chat(self) -> None:
        self.show_screen("chat")

    def action_show_agents(self) -> None:
        self.show_screen("agents")

    def action_show_tasks(self) -> None:
        self.show_screen("tasks")

    def action_show_voice(self) -> None:
        self.show_screen("voice")


def run_workspace(orchestrator, settings) -> None:
    """Run the opt-in V0.2 workspace and restore the terminal on exit."""
    CommandDeckTUI(orchestrator, settings).run()
