"""
NEUROCORE Unit Tests

This package contains comprehensive unit tests for the NEUROCORE AI assistant.

Test modules:
- test_model.py: Tests for OllamaModel class and Ollama API integration
- test_orchestrator.py: Tests for Orchestrator class and mode orchestration
- test_terminal.py: Tests for TerminalTool class and command execution
- test_memory.py: Tests for MemoryDatabase class and memory operations
- test_permissions.py: Tests for PermissionManager class and permission checking

Running tests:
    pytest tests/
    pytest tests/ -v
    pytest tests/ --cov=core --cov=tools --cov=memory --cov=voice
"""

__version__ = "0.1.0"
__author__ = "NEUROCORE Team"
