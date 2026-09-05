import logging
import os
import sys
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from core.config import load_settings
from core.modes import MODES
from core.orchestrator import Orchestrator
from interface.animations import startup, thinking
from interface.panels import banner, help_panel, message as render_message, model_info, status
from interface.theme import AI, ERROR, PRIMARY, SUCCESS, WARNING


console = Console()
logger = logging.getLogger(__name__)


def run_doctor():
    """Print real environment and local-service diagnostics without starting the UI."""
    import importlib.util
    import requests

    settings = load_settings()
    dependency_names = ("rich", "textual", "requests", "fastapi", "pydantic", "yaml")
    dependencies_ok = all(importlib.util.find_spec(name) for name in dependency_names)
    ollama_online = False
    model_ready = False
    try:
        response = requests.get(
            f"{settings.get('ollama_url', 'http://127.0.0.1:11434')}/api/tags",
            timeout=5,
        )
        response.raise_for_status()
        ollama_online = True
        models = {item.get("name") for item in response.json().get("models", [])}
        configured_model = settings.get("model", "qwen3:8b")
        model_ready = configured_model in models
    except (requests.RequestException, ValueError, KeyError):
        configured_model = settings.get("model", "qwen3:8b")

    console.print("[bold cyan]NEUROCORE ENVIRONMENT[/bold cyan]")
    console.print(f"Python       {'OK' if sys.version_info[:2] == (3, 11) else 'WARN'} · {sys.version.split()[0]}")
    console.print(f"Dependencies {'OK' if dependencies_ok else 'FAIL'}")
    console.print(f"Textual      {'OK' if importlib.util.find_spec('textual') else 'FAIL'}")
    console.print(f"Ollama       {'ONLINE' if ollama_online else 'OFFLINE'}")
    console.print(f"Model        {configured_model} · {'READY' if model_ready else 'NOT DETECTED'}")
    console.print(f"Sound        {'ENABLED' if settings.get('sound_enabled', False) else 'DISABLED'}")
    console.print("Tests        run `python -m pytest -q` to verify")
    return 0 if dependencies_ok else 1


def setup_logging(settings):
    """Configure logging based on settings."""
    
    logging_level = settings.get("logging_level", "INFO")
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add file handler
    log_file = os.path.join(logs_dir, "neurocore.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized: level={logging_level}, file={log_file}")


class NeuroCoreApp:

    def __init__(self):
        self.settings = load_settings()
        setup_logging(self.settings)
        logger.info("NeuroCoreApp initialized")
        self.orchestrator = Orchestrator(self.settings)
        self.modes = self.orchestrator.modes
        self.speech = None
        self.tts = None

    def initialize_voice(self):
        from voice.speech import SpeechRecognizer
        from voice.tts import TextToSpeech

        if self.speech is None:
            self.speech = SpeechRecognizer()
        if self.tts is None:
            self.tts = TextToSpeech()

    def current_mode(self):
        return self.modes.get()

    def show_banner(self):
        online = self.orchestrator.model.health_check()
        banner(console, self.settings, online)
        startup(console, ["Core system", "Configuration", "Security", "Ollama", "Model", "CLI", "System ready"])
        console.print(f"\n[{PRIMARY}]Type /help for commands.[/]")

    def show_help(self):
        help_panel(console)

    def voice_mode(self):
        self.initialize_voice()

        mode = self.modes.get("voice")

        console.print(
            f"\n[bold {mode.color}]🎙 NEUROCORE Voice Mode"
            f"[/bold {mode.color}]"
        )

        console.print(
            "[yellow]Say 'stop voice mode' or "
            "'குரல் நிறுத்து' to return.[/yellow]"
        )

        stop_commands = [
            "stop voice mode",
            "exit voice mode",
            "voice off",
            "turn off voice",
            "stop listening",
            "stop voice",

            "குரல் நிறுத்து",
            "குரல் நிறுத்துங்கள்",
            "வாய்ஸ் ஆஃப்",
            "வாய்ஸ் நிறுத்து",
            "வாய்ஸ் மோட் ஆஃப்",
            "வாய்ஸ் மோட் நிறுத்து",
        ]

        while True:

            try:

                text = self.speech.listen()

                if not text:
                    console.print(
                        "[yellow]I didn't hear anything.[/yellow]"
                    )
                    continue

                text = text.strip()

                console.print(
                    f"\n[bold green]You > [/bold green]{text}"
                )

                if any(
                    command in text.lower()
                    for command in stop_commands
                ):

                    console.print(
                        "\n[yellow]🔇 Voice mode stopped.[/yellow]"
                    )

                    self.tts.speak(
                        "Voice mode stopped. "
                        "குரல் பயன்முறை நிறுத்தப்பட்டது."
                    )

                    break

                answer = self.orchestrator.run(
                    text,
                    mode="voice"
                )

                console.print(
                    f"\n[bold cyan]NEUROCORE > [/bold cyan]"
                    f"{answer}"
                )

                self.tts.speak(answer)

            except KeyboardInterrupt:

                console.print(
                    "\n[yellow]🔇 Voice mode stopped.[/yellow]"
                )

                break

            except Exception as error:

                console.print(
                    f"[bold red]Voice Error:[/bold red] {error}"
                )

    def handle_command(self, message):
        lower = message.lower()

        if lower in {"exit", "quit"}:
            return "exit"

        if lower in {"/help", "help", "/?"}:
            self.show_help()
            return "continue"

        if lower in {"/status", "status"}:
            status(console, self.settings, self.orchestrator.model.health_check(), self.current_mode())
            return "continue"

        if lower in {"/model", "model"}:
            model_info(console, self.settings, self.orchestrator.model.health_check())
            return "continue"

        if lower == "/voice":
            self.voice_mode()
            return "continue"

        if lower == "/mode":
            mode = self.current_mode()
            console.print(
                f"Current mode: "
                f"[bold {mode.color}]{mode.label}"
                f"[/bold {mode.color}] — {mode.description}"
            )
            return "continue"

        if lower.startswith("/") and lower[1:] in MODES:
            self.modes.set(lower[1:])
            mode = self.current_mode()
            console.print(
                f"Mode set: "
                f"[bold {mode.color}]{mode.label}"
                f"[/bold {mode.color}] — {mode.description}"
            )
            return "continue"

        if message.startswith("/remember "):
            information = message[len("/remember "):].strip()

            if information:
                console.print(
                    f"[bold cyan]NEUROCORE > [/bold cyan]"
                    f"{self.orchestrator.remember(information)}"
                )

            return "continue"

        if lower == "/memory":
            memories = self.orchestrator.list_memories()

            if not memories:
                console.print(
                    "[yellow]No memories stored.[/yellow]"
                )
            else:
                console.print(
                    "\n[bold cyan]Long-term memory:[/bold cyan]"
                )
                for memory in memories:
                    console.print(
                        f"[green]•[/green] {memory[1]}"
                    )

            return "continue"

        if lower in {"/clear", "clear", "/reset"}:
            self.orchestrator.history.clear()
            console.print(f"[{SUCCESS}]✓ Conversation history cleared.[/]")
            return "continue"

        return None

    def run(self):
        self.show_banner()

        while True:

            try:

                mode = self.current_mode()

                message = console.input(
                    f"\n[bold {mode.color}]({mode.label})"
                    f"[/bold {mode.color}] "
                    f"[bold green]You > [/bold green]"
                )

                message = message.strip()

                if not message:
                    continue

                action = self.handle_command(message)

                if action == "exit":
                    console.print(
                        "[yellow]NEUROCORE shutting down.[/yellow]"
                    )
                    break

                if action == "continue":
                    continue

                render_message(console, "YOU", message, SUCCESS)
                with thinking(console):
                    tokens = self.orchestrator.stream_response(message, mode=mode.name)
                    response = ""
                    with Live("", console=console, refresh_per_second=12, transient=True) as live:
                        for token in tokens:
                            response += token
                            live.update(Markdown(response))
                render_message(console, f"NEUROCORE · {mode.label}", response, AI)

            except KeyboardInterrupt:

                console.print(
                    "\n[yellow]NEUROCORE stopped.[/yellow]"
                )

                break

            except Exception as error:

                logger.exception("CLI error")
                console.print(f"[{ERROR}]✕ {error}[/]")


if __name__ == "__main__":
    if "--doctor" in sys.argv:
        raise SystemExit(run_doctor())
    app = NeuroCoreApp()
    try:
        from interface.tui import run_tui
    except ImportError:
        run_tui = None
    if run_tui is None:
        app.run()
    else:
        run_tui(app.orchestrator, app.settings)