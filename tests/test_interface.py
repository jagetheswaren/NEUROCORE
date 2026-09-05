from types import SimpleNamespace
from unittest.mock import Mock

from rich.console import Console

from core.modes import ModeManager
from interface.panels import help_panel, model_info, status
from interface.sounds import SoundEngine
from interface.tui import NeuroCoreTUI
from main import NeuroCoreApp


def recorded_console():
    return Console(record=True, width=100, force_terminal=False)


def test_premium_panels_include_operational_details():
    console = recorded_console()
    help_panel(console)
    status(console, {"model": "qwen3:8b"}, True, ModeManager().get())
    model_info(console, {"model": "qwen3:8b", "ollama_url": "http://127.0.0.1:11434"}, True)

    output = console.export_text()
    assert "COMMANDS" in output
    assert "NEUROCORE STATUS" in output
    assert "qwen3:8b" in output
    assert "/status" in output


def test_cli_supports_plain_status_and_model_commands():
    app = NeuroCoreApp.__new__(NeuroCoreApp)
    app.settings = {"model": "qwen3:8b", "ollama_url": "http://127.0.0.1:11434"}
    app.orchestrator = SimpleNamespace(
        model=Mock(health_check=Mock(return_value=True)),
        history=[],
    )
    app.modes = ModeManager()

    assert app.handle_command("status") == "continue"
    assert app.handle_command("model") == "continue"
    assert app.handle_command("clear") == "continue"


def test_sound_engine_is_disabled_by_default():
    sounds = SoundEngine()
    assert sounds.status()["enabled"] is False
    assert sounds.play("ready") is False


def test_full_screen_tui_mounts_at_compact_size():
    class FakeModel:
        def health_check(self):
            return True

    class FakeOrchestrator:
        model = FakeModel()
        modes = ModeManager()
        history = []

    async def exercise():
        app = NeuroCoreTUI(FakeOrchestrator(), {"model": "qwen3:8b"})
        async with app.run_test(size=(40, 24)) as pilot:
            await pilot.pause()
            assert app.query_one("#conversation").display
            await pilot.press("ctrl+l")

    import asyncio
    asyncio.run(exercise())


def test_sound_assets_are_bundled():
    from pathlib import Path
    assets = Path("assets/sounds")
    assert {path.stem for path in assets.glob("*.wav")} == {
        "boot", "ready", "input", "thinking", "success", "warning", "error", "approval"
    }


def test_command_palette_and_settings_open():
    class FakeModel:
        def health_check(self):
            return True

    class FakeOrchestrator:
        model = FakeModel()
        modes = ModeManager()
        history = []

    async def exercise():
        app = NeuroCoreTUI(FakeOrchestrator(), {"model": "qwen3:8b"})
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.press("ctrl+p")
            assert app.screen.__class__.__name__ == "CommandPalette"
            await pilot.press("escape")
            app._handle_palette("settings")
            await pilot.pause()
            assert app.screen.__class__.__name__ == "SettingsModal"
            await pilot.press("escape")

    import asyncio
    asyncio.run(exercise())
