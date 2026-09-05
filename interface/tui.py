"""Full-screen Textual interface layered over the existing orchestrator."""

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Resize
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, RichLog, Static

from interface.sounds import SoundEngine
from interface.theme import AI, ERROR, MUTED, PRIMARY, SUCCESS, WARNING


class CommandPalette(ModalScreen[str | None]):
    CSS = """
    CommandPalette { align: center middle; background: rgba(0, 0, 0, 0.65); }
    #palette { width: 60; max-width: 90%; height: auto; border: round #00d9ff; background: #07121f; padding: 1; }
    #palette-list { height: 12; margin-top: 1; }
    """
    COMMANDS = ("Chat", "Projects", "Memory", "Knowledge", "Agents", "Tools",
                "Tasks", "Logs", "Settings", "Model", "Clear", "Sound", "Help", "Exit")

    def compose(self) -> ComposeResult:
        with Vertical(id="palette"):
            yield Label("◈ NEUROCORE COMMAND PALETTE", classes="title")
            yield Input(placeholder="Search commands...", id="palette-search")
            yield ListView(id="palette-list")

    def on_mount(self):
        self._refresh("")
        self.query_one("#palette-search", Input).focus()

    @on(Input.Changed, "#palette-search")
    def filter_commands(self, event: Input.Changed):
        self._refresh(event.value)

    def _refresh(self, query):
        items = self.query_one("#palette-list", ListView)
        items.clear()
        for command in self.COMMANDS:
            if query.lower() in command.lower():
                items.append(ListItem(Label(f"▶ {command}"), name=command.lower()))

    @on(ListView.Selected, "#palette-list")
    def select_command(self, event: ListView.Selected):
        self.dismiss(event.item.name)

    def key_escape(self):
        self.dismiss(None)

    def key_enter(self):
        items = self.query_one("#palette-list", ListView)
        if items.highlighted_child:
            self.dismiss(items.highlighted_child.name)


class SettingsModal(ModalScreen[None]):
    CSS = """
    SettingsModal { align: center middle; background: rgba(0, 0, 0, 0.65); }
    #settings { width: 68; max-width: 90%; height: auto; border: round #7d4ac7; background: #07121f; padding: 1; }
    """

    def __init__(self, settings, online, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.online = online

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("◈ NEUROCORE SETTINGS", classes="title"),
            Static(self._content(), id="settings-content"),
            Label("Press Escape to close", classes="muted"),
            id="settings",
        )

    def _content(self):
        return (
            "[bold cyan]GENERAL[/]\n"
            f"Animation       {'REDUCED' if self.settings.get('reduced_motion', False) else 'ON'}\n"
            f"Reduced motion  {'ON' if self.settings.get('reduced_motion', False) else 'OFF'}\n\n"
            "[bold cyan]SOUND[/]\n"
            f"Enabled         {'ON' if self.settings.get('sound_enabled', False) else 'OFF'}\n"
            f"Volume          {self.settings.get('sound_volume', 0.2):.2f}\n\n"
            "[bold cyan]MODEL[/]\n"
            f"Provider        Ollama\nModel           {self.settings.get('model', 'qwen3:8b')}\n"
            f"Status          {'CONNECTED' if self.online else 'UNAVAILABLE'}\n\n"
            "[bold cyan]SECURITY[/]\nPermission      Approval-controlled"
        )


class NeuroCoreTUI(App):
    """Responsive cyber HUD for NEUROCORE V0.1."""

    CSS = """
    Screen { background: #07121f; color: #d7f9ff; }
    #body { height: 1fr; }
    #nav { width: 20; border: round #176b87; padding: 1; }
    #center { width: 1fr; border: round #7d4ac7; padding: 1; }
    #hud { width: 24; border: round #176b87; padding: 1; }
    #conversation { height: 1fr; scrollbar-size: 1 1; }
    #input { dock: bottom; margin: 1 0 0 0; border: round #00d9ff; }
    .title { color: #00d9ff; text-style: bold; }
    .muted { color: #7295a3; }
    .ai { color: #d68cff; }
    .ok { color: #42f58d; }
    .warn { color: #ffd166; }
    """

    BINDINGS = [
        ("ctrl+l", "redraw", "Redraw"),
        ("ctrl+p", "palette", "Command palette"),
        ("ctrl+c", "quit", "Exit"),
    ]

    def __init__(self, orchestrator, settings, **kwargs):
        super().__init__(**kwargs)
        self.orchestrator = orchestrator
        self.settings = settings
        self.sound = SoundEngine(
            settings.get("sound_enabled", False),
            settings.get("sound_volume", 0.2),
        )
        self.online = False
        self.mode = orchestrator.modes.get()
        self.state = "IDLE"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="body"):
            yield Vertical(
                Static("◈ NAVIGATION", classes="title"),
                Static("▶ CHAT\n  PROJECTS\n  MEMORY\n  KNOWLEDGE\n  AGENTS\n  TOOLS\n  TASKS\n  LOGS\n  SETTINGS", classes="muted"),
                id="nav",
            )
            with Vertical(id="center"):
                yield Static("◉ NEURAL CORE", classes="title")
                yield Static("◈ NEURAL CORE // IDLE", id="core-state", classes="ai")
                yield RichLog(id="conversation", markup=True, wrap=True)
                yield Input(placeholder="❯ Ask NEUROCORE anything...", id="input")
            yield Vertical(
                Static("◈ SYSTEM HUD", classes="title"),
                Static(id="hud-content"),
                id="hud-pane",
            )
        yield Footer()

    def on_mount(self):
        self._render_hud()
        self.query_one("#conversation", RichLog).write("[cyan]NEUROCORE ONLINE[/cyan]")
        self.query_one("#conversation", RichLog).write("[dim]Type a message. Ctrl+P opens commands.[/dim]")
        self.query_one("#input", Input).focus()
        self.check_connection()

    def on_resize(self, event: Resize):
        compact = event.size.width < 80
        self.query_one("#nav").display = not compact
        self.query_one("#hud-pane").display = not compact

    def _render_hud(self):
        state = "ONLINE" if self.online else "CONNECTING"
        state_class = "ok" if self.online else "warn"
        hud = self.query_one("#hud-content", Static)
        hud.update(
            f"[{state_class}]CORE     ● {state}[/]\n"
            f"[{state_class}]LLM      ● {'CONNECTED' if self.online else 'CHECKING'}[/]\n"
            "[cyan]OLLAMA   ● LOCAL[/]\n"
            "[cyan]SECURITY ● ACTIVE[/]\n\n"
            f"[bold]MODEL[/bold]\n{self.settings.get('model', 'qwen3:8b')}\n\n"
            "[bold]SESSION[/bold]\nACTIVE\n\n"
            f"[bold]MODE[/bold]\n{self.mode.label}"
        )
        self.query_one("#core-state", Static).update(f"◈ NEURAL CORE // {self.state}")

    @work(exclusive=True, thread=True)
    def check_connection(self):
        self.online = self.orchestrator.model.health_check()
        self.call_from_thread(self._render_hud)

    @on(Input.Submitted)
    def submit(self, event: Input.Submitted):
        text = event.value.strip()
        event.input.value = ""
        if not text:
            return
        if text.lower() in {"exit", "quit"}:
            self.exit()
            return
        if text.lower() == "/settings":
            self.push_screen(SettingsModal(self.settings, self.online))
            return
        if text.lower() in {"/help", "help"}:
            self._write("[cyan]Commands:[/] /help /status /model /clear /sound on|off /exit")
            return
        if text.lower() in {"/status", "status"}:
            self._render_hud()
            self._write("[cyan]Status refreshed.[/cyan]")
            return
        if text.lower() in {"/model", "model"}:
            self._write(
                f"[cyan]Provider:[/] Ollama  "
                f"[cyan]Model:[/] {self.settings.get('model', 'qwen3:8b')}  "
                f"[cyan]Connection:[/] {'Connected' if self.online else 'Unavailable'}"
            )
            return
        if text.lower() in {"/clear", "clear"}:
            self.orchestrator.history.clear()
            self.query_one("#conversation", RichLog).clear()
            self._write("[green]✓ Conversation cleared[/green]")
            return
        if text.lower() in {"/sound on", "/sound off"}:
            self.sound.set_enabled(text.lower().endswith("on"))
            self._write(f"[cyan]Sound {'enabled' if self.sound.enabled else 'disabled'}[/cyan]")
            return
        if text.lower() == "/sound status":
            state = self.sound.status()
            self._write(f"[cyan]Sound:[/] {'ON' if state['enabled'] else 'OFF'} · volume {state['volume']:.2f}")
            return
        self._write(f"[bold green]YOU[/bold green]  {text}")
        self._set_state("THINKING")
        self.stream_response(text)

    def _write(self, content):
        self.query_one("#conversation", RichLog).write(content)

    @work(thread=True, exclusive=True)
    def stream_response(self, text):
        self.call_from_thread(self._write, "[magenta]◐ NEUROCORE is processing...[/magenta]")
        response = ""
        try:
            for token in self.orchestrator.stream_response(text, mode=self.mode.name):
                response += token
                self.call_from_thread(self._replace_last, response)
            self.call_from_thread(self._write, "[green]✓ Response complete[/green]")
            self.call_from_thread(self._set_state, "SUCCESS")
        except Exception as error:
            self.call_from_thread(self._write, f"[red]✕ {error}[/red]")
            self.call_from_thread(self._set_state, "ERROR")

    def _replace_last(self, response):
        log = self.query_one("#conversation", RichLog)
        log.write(f"[magenta]NEUROCORE[/magenta]  {response}")

    def action_redraw(self):
        self.refresh(layout=True)

    def action_palette(self):
        self.push_screen(CommandPalette(), self._handle_palette)

    def _handle_palette(self, command):
        if command == "exit":
            self.exit()
        elif command == "settings":
            self.push_screen(SettingsModal(self.settings, self.online))
        elif command == "clear":
            self.orchestrator.history.clear()
            self.query_one("#conversation", RichLog).clear()
        elif command == "model":
            self._write(f"[cyan]Model:[/] {self.settings.get('model', 'qwen3:8b')}")
        elif command == "help":
            self._write("[cyan]Commands:[/] /help /status /model /clear /settings /sound /exit")

    def _set_state(self, state):
        self.state = state
        if self.query("#core-state"):
            self.query_one("#core-state", Static).update(f"◈ NEURAL CORE // {state}")


def run_tui(orchestrator, settings):
    """Run the full-screen UI and restore terminal state on exit."""
    NeuroCoreTUI(orchestrator, settings).run()
