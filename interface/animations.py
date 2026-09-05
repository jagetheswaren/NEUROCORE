"""Short, capability-safe terminal animations."""

import time
from contextlib import contextmanager

from rich.status import Status


@contextmanager
def thinking(console, message="NEUROCORE is processing..."):
    """Show a subtle spinner without delaying or exposing model reasoning."""
    status = Status(message, spinner="dots", console=console)
    status.start()
    try:
        yield
    finally:
        status.stop()


def startup(console, steps):
    """Render a quick startup checklist."""
    for label in steps:
        console.print(f"[bright_green]✓[/bright_green] {label}")
        time.sleep(0.03)
