"""
Unit tests for core/orchestrator.py - Orchestrator class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.orchestrator import Orchestrator
from core.model import OllamaModelError


class TestOrchestrator:
    """Test Orchestrator class."""

    def test_init(self, settings, mock_requests):
        """Test Orchestrator initialization."""
        orchestrator = Orchestrator(settings)
        assert orchestrator.model is not None
        assert orchestrator.memory is not None
        assert orchestrator.terminal is not None
        assert orchestrator.permissions is not None
        assert orchestrator.modes is not None
        assert len(orchestrator.history) == 0

    def test_run_friend_mode(self, settings, mock_requests):
        """Test running orchestrator in friend mode."""
        orchestrator = Orchestrator(settings)
        orchestrator.modes.set("friend")
        response = orchestrator.run("Hello", mode="friend")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_run_terminal_mode_auto_approve(self, settings, mock_requests, mock_subprocess):
        """Test terminal mode with auto-approved command."""
        orchestrator = Orchestrator(settings)
        orchestrator.modes.set("terminal")
        # Auto-approved command should execute without asking
        with patch.object(orchestrator.terminal, "run", return_value=(0, "output")):
            response = orchestrator.run("$ pwd", mode="terminal")
            assert isinstance(response, str)

    def test_run_plan_mode(self, settings, mock_requests):
        """Test running orchestrator in plan mode."""
        orchestrator = Orchestrator(settings)
        orchestrator.modes.set("plan")
        response = orchestrator.run("How should I organize my code?", mode="plan")
        assert isinstance(response, str)

    def test_run_with_ollama_error(self, settings):
        """Test error handling when Ollama fails."""
        orchestrator = Orchestrator(settings)
        with patch.object(orchestrator.model, "_request") as mock_request:
            mock_request.side_effect = OllamaModelError("Ollama server is down")
            response = orchestrator.run("Hello", mode="friend")
            # Response should contain error message
            assert isinstance(response, str)
            assert len(response) > 0

    def test_run_with_general_exception(self, settings, mock_requests):
        """Test error handling for general exceptions."""
        orchestrator = Orchestrator(settings)
        with patch.object(orchestrator.model, "chat") as mock_chat:
            mock_chat.side_effect = Exception("Unexpected error")
            response = orchestrator.run("Hello", mode="friend")
            assert isinstance(response, str)

    def test_remember(self, settings, mock_requests):
        """Test saving to long-term memory."""
        orchestrator = Orchestrator(settings)
        result = orchestrator.remember("Important information")
        assert isinstance(result, str)
        assert "saved" in result.lower() or "remember" in result.lower()

    def test_list_memories(self, settings, mock_requests):
        """Test listing memories."""
        orchestrator = Orchestrator(settings)
        # Add some memories
        orchestrator.remember("Memory 1")
        orchestrator.remember("Memory 2")
        memories = orchestrator.list_memories()
        assert isinstance(memories, list)

    def test_conversation_history(self, settings, mock_requests):
        """Test conversation history management."""
        orchestrator = Orchestrator(settings)
        assert len(orchestrator.history) == 0
        orchestrator.run("Hello", mode="friend")
        # History should have at least user message
        assert len(orchestrator.history) > 0

    def test_clear_history(self, settings, mock_requests):
        """Test clearing conversation history."""
        orchestrator = Orchestrator(settings)
        orchestrator.run("Hello", mode="friend")
        assert len(orchestrator.history) > 0
        orchestrator.history.clear()
        assert len(orchestrator.history) == 0

    def test_mode_switching(self, settings, mock_requests):
        """Test switching between modes."""
        orchestrator = Orchestrator(settings)
        
        # Start in friend mode
        orchestrator.modes.set("friend")
        assert orchestrator.modes.get().name == "friend"
        
        # Switch to plan mode
        orchestrator.modes.set("plan")
        assert orchestrator.modes.get().name == "plan"
        
        # Switch to terminal mode
        orchestrator.modes.set("terminal")
        assert orchestrator.modes.get().name == "terminal"
