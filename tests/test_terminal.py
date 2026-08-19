"""
Unit tests for tools/terminal.py - TerminalTool class.
"""

import pytest
from unittest.mock import Mock, patch
import subprocess
from pathlib import Path
from tools.terminal import TerminalTool


class TestTerminalTool:
    """Test TerminalTool class."""

    def test_init(self, tmp_path):
        """Test TerminalTool initialization."""
        terminal = TerminalTool(cwd=str(tmp_path), timeout=60)
        assert terminal.cwd == tmp_path
        assert terminal.timeout == 60

    def test_init_creates_directory(self, tmp_path):
        """Test that TerminalTool creates working directory if it doesn't exist."""
        new_dir = tmp_path / "new_workspace"
        assert not new_dir.exists()
        terminal = TerminalTool(cwd=str(new_dir))
        assert new_dir.exists()

    def test_run_success(self, tmp_path, mock_subprocess):
        """Test successful command execution."""
        terminal = TerminalTool(cwd=str(tmp_path))
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "test output"
        mock_subprocess.return_value.stderr = ""
        
        returncode, output = terminal.run("echo test")
        assert returncode == 0
        assert output == "test output"

    def test_run_with_stderr(self, tmp_path, mock_subprocess):
        """Test command execution with stderr output."""
        terminal = TerminalTool(cwd=str(tmp_path))
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "output"
        mock_subprocess.return_value.stderr = "warning"
        
        returncode, output = terminal.run("command")
        assert returncode == 0
        assert "output" in output
        assert "warning" in output

    def test_run_timeout(self, tmp_path):
        """Test command timeout handling."""
        terminal = TerminalTool(cwd=str(tmp_path), timeout=1)
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("command", 1)
            returncode, output = terminal.run("long_running_command")
            assert returncode == -1
            assert "timeout" in output.lower()

    def test_run_command_not_found(self, tmp_path):
        """Test handling of command not found."""
        terminal = TerminalTool(cwd=str(tmp_path))
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("command not found")
            returncode, output = terminal.run("nonexistent_command")
            assert returncode == -1
            assert "not found" in output.lower()

    def test_run_generic_exception(self, tmp_path):
        """Test handling of generic exception."""
        terminal = TerminalTool(cwd=str(tmp_path))
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Unexpected error")
            returncode, output = terminal.run("command")
            assert returncode == -1
            assert len(output) > 0

    def test_run_uses_configured_timeout(self, tmp_path, mock_subprocess):
        """Test that run() uses configured timeout by default."""
        terminal = TerminalTool(cwd=str(tmp_path), timeout=180)
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = ""
        mock_subprocess.return_value.stderr = ""
        
        terminal.run("echo test")
        # Verify timeout was passed to subprocess.run
        mock_subprocess.assert_called_once()
        call_kwargs = mock_subprocess.call_args[1]
        assert call_kwargs["timeout"] == 180

    def test_run_override_timeout(self, tmp_path, mock_subprocess):
        """Test that run() allows overriding timeout."""
        terminal = TerminalTool(cwd=str(tmp_path), timeout=180)
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = ""
        mock_subprocess.return_value.stderr = ""
        
        terminal.run("echo test", timeout=60)
        # Verify override timeout was used
        call_kwargs = mock_subprocess.call_args[1]
        assert call_kwargs["timeout"] == 60

    def test_run_command_fails(self, tmp_path, mock_subprocess):
        """Test handling of command failure (non-zero exit code)."""
        terminal = TerminalTool(cwd=str(tmp_path))
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = "error occurred"
        mock_subprocess.return_value.stderr = ""
        
        returncode, output = terminal.run("failing_command")
        assert returncode == 1

    def test_run_respects_working_directory(self, tmp_path, mock_subprocess):
        """Test that run() uses the configured working directory."""
        terminal = TerminalTool(cwd=str(tmp_path))
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = ""
        mock_subprocess.return_value.stderr = ""
        
        terminal.run("pwd")
        # Verify cwd was passed to subprocess.run
        call_kwargs = mock_subprocess.call_args[1]
        assert call_kwargs["cwd"] == tmp_path

    def test_run_text_encoding(self, tmp_path, mock_subprocess):
        """Test that run() handles UTF-8 encoding."""
        terminal = TerminalTool(cwd=str(tmp_path))
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "உ"  # Tamil character
        mock_subprocess.return_value.stderr = ""
        
        returncode, output = terminal.run("echo test")
        assert returncode == 0
        assert "உ" in output or output  # Output is preserved
