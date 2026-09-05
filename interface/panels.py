"""Rich renderers for the premium NEUROCORE terminal layout."""

from rich.align import Align
from rich.box import ROUNDED, SIMPLE
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from interface.theme import AI, ACCENT, MUTED, PRIMARY, SUCCESS, WARNING


def banner(console, settings, online):
    model = settings.get("model", "qwen3:8b")
    state = "ONLINE" if online else "OFFLINE"
    state_style = SUCCESS if online else WARNING
    title = Text("NEUROCORE", style=f"bold {PRIMARY}")
    subtitle = Text("PERSONAL AI AGENT", style=f"bold {MUTED}")
    body = Text.assemble(title, "\n", subtitle)
    body.justify = "center"
    console.print(Panel(Align.center(body), border_style=PRIMARY, box=ROUNDED))
    console.print(
        f"[bold {PRIMARY}]NEUROCORE[/bold {PRIMARY}] v0.4  "
        f"[{MUTED}]│[/] Ollama  [{MUTED}]│[/] {model}  "
        f"[{state_style}]● {state}[/]"
    )


def status(console, settings, online, mode):
    table = Table(title="NEUROCORE STATUS", box=SIMPLE, title_style=f"bold {PRIMARY}")
    table.add_column("Subsystem", style=MUTED)
    table.add_column("State")
    table.add_row("Core", f"[{SUCCESS}]● ONLINE[/]")
    table.add_row("LLM", f"[{SUCCESS if online else WARNING}]● {'CONNECTED' if online else 'UNAVAILABLE'}[/]")
    table.add_row("Provider", "Ollama")
    table.add_row("Model", settings.get("model", "qwen3:8b"))
    table.add_row("Security", f"[{SUCCESS}]● ACTIVE[/]")
    table.add_row("Session", f"[{ACCENT}]ACTIVE · {mode.label}[/]")
    console.print(Panel(table, border_style=ACCENT, box=ROUNDED))


def model_info(console, settings, online):
    table = Table(title="LLM INFORMATION", box=SIMPLE, title_style=f"bold {AI}")
    table.add_column("Property", style=MUTED)
    table.add_column("Value")
    table.add_row("Provider", "Ollama")
    table.add_row("Model", settings.get("model", "qwen3:8b"))
    table.add_row("Endpoint", settings.get("ollama_url", "http://127.0.0.1:11434"))
    table.add_row("Connection", f"[{SUCCESS if online else WARNING}]{'Connected' if online else 'Unavailable'}[/]")
    console.print(Panel(table, border_style=AI, box=ROUNDED))


def help_panel(console):
    table = Table(title="COMMANDS", box=SIMPLE, title_style=f"bold {PRIMARY}")
    table.add_column("Command", style=PRIMARY)
    table.add_column("Purpose")
    rows = [
        ("/help", "Show available commands"),
        ("/status", "Show live system status"),
        ("/model", "Show active LLM configuration"),
        ("/clear", "Clear conversation history"),
        ("/friend /plan /terminal /build", "Switch operating mode"),
        ("/remember <text>", "Save long-term memory"),
        ("/memory", "List stored memories"),
        ("/voice", "Start voice conversation"),
        ("exit / quit", "Exit NEUROCORE"),
    ]
    for command, purpose in rows:
        table.add_row(command, purpose)
    console.print(Panel(table, border_style=PRIMARY, box=ROUNDED))


def message(console, speaker, content, style):
    console.print(
        Panel(content, title=f" {speaker} ", title_align="left",
              border_style=style, box=ROUNDED, padding=(0, 1))
    )
