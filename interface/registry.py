"""Shared screen metadata for the V0.2 workspace and command palette."""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class WorkspaceScreen:
    key: str
    title: str
    shortcut: str
    description: str


SCREENS = (
    WorkspaceScreen("dashboard", "Dashboard", "D", "System overview and active run"),
    WorkspaceScreen("chat", "Chat", "C", "Conversation with NEUROCORE"),
    WorkspaceScreen("agents", "Agents", "A", "Agent registry and capabilities"),
    WorkspaceScreen("tasks", "Tasks", "T", "Plans, approvals, and execution"),
    WorkspaceScreen("voice", "Voice", "V", "Voice capability and language lab"),
    WorkspaceScreen("projects", "Projects", "P", "Project workspaces"),
    WorkspaceScreen("memory", "Memory", "M", "Persistent context"),
    WorkspaceScreen("settings", "Settings", "S", "Runtime preferences"),
)


def get_screen(key: str) -> WorkspaceScreen:
    for screen in SCREENS:
        if screen.key == key:
            return screen
    raise KeyError(f"Unknown workspace screen: {key}")
