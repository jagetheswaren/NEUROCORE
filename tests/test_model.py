"""
Unit tests for core/model.py - OllamaModel class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from core.model import OllamaModel, OllamaModelError


class TestOllamaModel:
    """Test OllamaModel class."""

    def test_init(self, settings):
        """Test OllamaModel initialization."""
        model = OllamaModel(settings)
        assert model.url == "http://127.0.0.1:11434/api/chat"
        assert model.model_name == "qwen3:8b"
        assert model.temperature == 0.7
        assert model.timeout == 300

    def test_request_success(self, mock_requests, settings, mock_ollama_response):
        """Test successful API request."""
        model = OllamaModel(settings)
        response = model._request("test message")
        assert response == "This is a test response from Ollama."
        mock_requests.assert_called_once()

    def test_request_connection_error(self, settings):
        """Test handling of connection error."""
        model = OllamaModel(settings)
        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.ConnectionError("Connection failed")
            with pytest.raises(OllamaModelError) as exc_info:
                model._request("test message")
            assert "Could not connect to Ollama" in str(exc_info.value)

    def test_request_timeout(self, settings):
        """Test handling of timeout."""
        model = OllamaModel(settings)
        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.Timeout("Request timed out")
            with pytest.raises(OllamaModelError) as exc_info:
                model._request("test message")
            assert "Ollama is overloaded" in str(exc_info.value)

    def test_request_404_not_found(self, settings):
        """Test handling of 404 error (model not found)."""
        model = OllamaModel(settings)
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Model not found"
            mock_post.return_value = mock_response
            with pytest.raises(OllamaModelError) as exc_info:
                model._request("test message")
            assert "Model not found" in str(exc_info.value)
            assert "ollama pull" in str(exc_info.value)

    def test_request_http_error(self, settings):
        """Test handling of HTTP error."""
        model = OllamaModel(settings)
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_post.return_value = mock_response
            with pytest.raises(OllamaModelError) as exc_info:
                model._request("test message")
            assert "Ollama server error" in str(exc_info.value)

    def test_request_malformed_response(self, settings):
        """Test handling of malformed response."""
        model = OllamaModel(settings)
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_post.return_value = mock_response
            with pytest.raises(OllamaModelError) as exc_info:
                model._request("test message")
            assert "Malformed response" in str(exc_info.value)

    def test_health_check_success(self, mock_requests, settings):
        """Test successful health check."""
        model = OllamaModel(settings)
        with patch.object(model, "_request", return_value="OK"):
            health = model.health_check()
            assert health is True

    def test_health_check_failure(self, settings):
        """Test failed health check."""
        model = OllamaModel(settings)
        with patch.object(model, "_request", side_effect=OllamaModelError("Server down")):
            health = model.health_check()
            assert health is False

    def test_chat_simple_message(self, mock_requests, settings):
        """Test simple chat message."""
        model = OllamaModel(settings)
        response = model.chat("Hello")
        assert response == "This is a test response from Ollama."

    def test_chat_with_history(self, mock_requests, settings):
        """Test chat with conversation history."""
        model = OllamaModel(settings)
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        response = model.chat("How are you?", history)
        assert response == "This is a test response from Ollama."

    def test_ollama_model_error_custom_exception(self):
        """Test OllamaModelError custom exception."""
        error = OllamaModelError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
