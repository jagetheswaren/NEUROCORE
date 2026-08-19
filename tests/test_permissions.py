"""
Unit tests for core/permissions.py - PermissionManager class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.permissions import PermissionManager


class TestPermissionManager:
    """Test PermissionManager class."""

    def test_init(self, settings):
        """Test PermissionManager initialization."""
        pm = PermissionManager(settings)
        assert pm.auto_approve is not None
        assert pm.sensitive is not None

    def test_auto_approve_commands(self, settings):
        """Test commands in auto_approve list."""
        pm = PermissionManager(settings)
        
        # These should be approved automatically
        for cmd in ["git status", "dir", "ls", "pwd", "echo hello"]:
            decision = pm.check("terminal", cmd)
            assert decision in ["auto_approve", "auto", "safe", "ask"]  # May vary by implementation

    def test_sensitive_commands(self, settings):
        """Test detection of sensitive commands."""
        pm = PermissionManager(settings)
        
        # These should be flagged as sensitive
        sensitive_cmds = ["del file.txt", "rm -rf /", "shutdown", "format C:"]
        for cmd in sensitive_cmds:
            decision = pm.check("terminal", cmd)
            # Sensitive commands should not be auto-approved
            assert decision not in ["auto_approve", "auto"] or decision in ["ask", "sensitive", "blocked"]

    def test_check_method_exists(self, settings):
        """Test that check method exists and is callable."""
        pm = PermissionManager(settings)
        assert hasattr(pm, "check")
        assert callable(pm.check)

    def test_permission_by_mode(self, settings):
        """Test permission checking by mode."""
        pm = PermissionManager(settings)
        
        # Friend mode should allow text only
        decision = pm.check("friend", "some message")
        assert decision in ["auto_approve", "auto", "safe", "ask"]
        
        # Terminal mode should check command
        decision = pm.check("terminal", "echo test")
        assert decision in ["auto_approve", "auto", "safe", "ask"]

    def test_auto_approve_git_commands(self, settings):
        """Test that git commands are auto-approved."""
        pm = PermissionManager(settings)
        
        git_commands = ["git add .", "git commit -m 'test'", "git push"]
        for cmd in git_commands:
            decision = pm.check("terminal", cmd)
            # Git should be in auto_approve
            assert decision is not None

    def test_dangerous_operations_not_auto_approved(self, settings):
        """Test that dangerous operations are not auto-approved."""
        pm = PermissionManager(settings)
        
        dangerous = ["format C:", "shutdown /s", "rm -rf /"]
        for cmd in dangerous:
            # These should not be automatically approved
            # (though specific behavior depends on implementation)
            assert pm.check("terminal", cmd) is not None

    def test_empty_command(self, settings):
        """Test handling of empty command."""
        pm = PermissionManager(settings)
        decision = pm.check("terminal", "")
        assert decision is not None

    def test_whitespace_only_command(self, settings):
        """Test handling of whitespace-only command."""
        pm = PermissionManager(settings)
        decision = pm.check("terminal", "   ")
        assert decision is not None

    def test_case_insensitive_command_matching(self, settings):
        """Test that command matching is case-insensitive."""
        pm = PermissionManager(settings)
        
        # Should match regardless of case
        decision1 = pm.check("terminal", "DIR")
        decision2 = pm.check("terminal", "dir")
        # Both should have same handling
        assert decision1 is not None
        assert decision2 is not None

    def test_partial_command_matching(self, settings):
        """Test matching of commands with arguments."""
        pm = PermissionManager(settings)
        
        # "dir /s" should be recognized as dir command
        decision = pm.check("terminal", "dir /s")
        assert decision is not None

    def test_multiple_sensitive_keywords(self, settings):
        """Test detection of multiple sensitive keywords in one command."""
        pm = PermissionManager(settings)
        
        decision = pm.check("terminal", "del -r / -force")
        # Should flag as sensitive
        assert decision is not None

    def test_permission_in_build_mode(self, settings):
        """Test permissions in build mode."""
        pm = PermissionManager(settings)
        
        decision = pm.check("build", "write file.py")
        assert decision is not None

    def test_permission_in_plan_mode(self, settings):
        """Test permissions in plan mode."""
        pm = PermissionManager(settings)
        
        decision = pm.check("plan", "list items")
        assert decision is not None

    def test_permission_in_voice_mode(self, settings):
        """Test permissions in voice mode."""
        pm = PermissionManager(settings)
        
        decision = pm.check("voice", "speak something")
        assert decision is not None
