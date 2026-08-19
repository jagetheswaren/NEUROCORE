import logging
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.config import load_settings
from core.modes import MODES
from core.orchestrator import Orchestrator
from voice.speech import SpeechRecognizer
from voice.tts import TextToSpeech


console = Console()
logger = logging.getLogger(__name__)


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
        if self.speech is None:
            self.speech = SpeechRecognizer()
        if self.tts is None:
            self.tts = TextToSpeech()

    def current_mode(self):
        return self.modes.get()

    def show_banner(self):
        console.print(
            Panel.fit(
                "[bold cyan]NEUROCORE v0.4[/bold cyan]\n"
                "One Brain • Modes • Memory • Voice\n"
                f"Model: {self.settings.get('model', 'qwen3:8b')}\n\n"
                "[yellow]Commands:[/yellow] "
                "/friend /plan /terminal /build /voice "
                "/mode /remember /memory /clear /help /exit",
                title="NEUROCORE"
            )
        )

    def show_help(self):
        table = Table(title="NEUROCORE Commands")
        table.add_column("Command")
        table.add_column("Purpose")

        table.add_row("/friend", "Switch to Friend mode (chat)")
        table.add_row("/plan", "Switch to Plan mode (no changes)")
        table.add_row("/terminal", "Switch to Terminal mode ($ to run)")
        table.add_row("/build", "Switch to Build mode")
        table.add_row("/voice", "Start voice conversation")
        table.add_row("/mode", "Show current mode")
        table.add_row("/remember <info>", "Save long-term memory")
        table.add_row("/memory", "List memories")
        table.add_row("/clear", "Clear conversation history")
        table.add_row("/help", "Show this help")
        table.add_row("exit", "Quit NEUROCORE")

        console.print(table)

        console.print(
            "\n[yellow]Terminal mode:[/yellow] type "
            "[bold]$ dir[/bold] to run a command safely."
        )

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

        if lower in {"/help", "/?"}:
            self.show_help()
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

        if lower in {"/clear", "/reset"}:
            self.orchestrator.history.clear()
            console.print(
                "[yellow]Conversation history cleared.[/yellow]"
            )
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

                answer = self.orchestrator.run(
                    message,
                    mode=mode.name
                )

                console.print(
                    f"\n[bold {mode.color}]NEUROCORE "
                    f"({mode.label}) > [/bold {mode.color}]"
                    f"{answer}"
                )

            except KeyboardInterrupt:

                console.print(
                    "\n[yellow]NEUROCORE stopped.[/yellow]"
                )

                break

            except Exception as error:

                console.print(
                    f"[bold red]Error:[/bold red] {error}"
                )


if __name__ == "__main__":
    NeuroCoreApp().run()