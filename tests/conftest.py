"""
pytest fixtures and configuration for NEUROCORE tests.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    yield db_path
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def settings():
    """Provide default test settings."""
    return {
        "model": "qwen3:8b",
        "ollama_url": "http://127.0.0.1:11434",
        "temperature": 0.7,
        "ollama_timeout": 300,
        "command_timeout": 120,
        "logging_level": "INFO",
        "workspace": "workspace",
        "auto_approve": ["git", "dir", "ls", "pwd", "echo"],
        "sensitive": ["del", "rm", "shutdown", "format"],
    }


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response."""
    return {
        "model": "qwen3:8b",
        "created_at": "2024-01-01T00:00:00.000000000Z",
        "message": {
            "role": "assistant",
            "content": "This is a test response from Ollama."
        },
        "done": True,
        "total_duration": 1000000000,
        "load_duration": 500000000,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 300000000,
        "eval_count": 5,
        "eval_duration": 200000000
    }


@pytest.fixture
def mock_requests(mock_ollama_response):
    """Mock requests library for Ollama API calls."""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ollama_response
        mock_response.text = json.dumps(mock_ollama_response)
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for terminal command execution."""
    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "command output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        yield mock_run


@pytest.fixture
def mock_memory_db(temp_db):
    """Mock memory database for testing."""
    with patch("memory.database.DB_PATH", temp_db):
        from memory.database import MemoryDatabase
        db = MemoryDatabase()
        yield db
        db.close()


@pytest.fixture
def mock_speech_recognizer():
    """Mock speech recognizer."""
    with patch("voice.speech.WhisperModel"):
        from voice.speech import SpeechRecognizer
        with patch.object(SpeechRecognizer, "listen", return_value="test input"):
            recognizer = SpeechRecognizer()
            yield recognizer


@pytest.fixture
def mock_tts():
    """Mock text-to-speech."""
    with patch("voice.tts.winsound"):
        from voice.tts import TextToSpeech
        with patch.object(TextToSpeech, "speak"):
            tts = TextToSpeech()
            yield tts
