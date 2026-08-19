"""
Unit tests for memory/database.py - MemoryDatabase class.
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from memory.database import MemoryDatabase


class TestMemoryDatabase:
    """Test MemoryDatabase class."""

    def test_init_success(self, temp_db):
        """Test successful database initialization."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            assert db.connection is not None
            db.close()

    def test_create_tables(self, temp_db):
        """Test that tables are created on initialization."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            
            # Verify table exists
            cursor = db.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='memories'"
            )
            assert cursor.fetchone() is not None
            db.close()

    def test_save_memory(self, temp_db):
        """Test saving a memory."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            db.save("Test memory content", category="general")
            
            # Verify memory was saved
            cursor = db.connection.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            assert count == 1
            db.close()

    def test_save_multiple_memories(self, temp_db):
        """Test saving multiple memories."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            db.save("Memory 1", category="general")
            db.save("Memory 2", category="important")
            db.save("Memory 3", category="note")
            
            cursor = db.connection.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            assert count == 3
            db.close()

    def test_get_all_memories(self, temp_db):
        """Test retrieving all memories."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            db.save("Memory 1")
            db.save("Memory 2")
            
            memories = db.get_all()
            assert len(memories) == 2
            assert memories[0][1] == "Memory 2"  # Most recent first (DESC)
            assert memories[1][1] == "Memory 1"
            db.close()

    def test_get_all_empty(self, temp_db):
        """Test retrieving memories when database is empty."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            memories = db.get_all()
            assert len(memories) == 0
            db.close()

    def test_save_with_category(self, temp_db):
        """Test saving memory with custom category."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            db.save("Important fact", category="facts")
            
            memories = db.get_all()
            assert len(memories) == 1
            assert memories[0][1] == "Important fact"
            assert memories[0][2] == "facts"
            db.close()

    def test_close_connection(self, temp_db):
        """Test closing database connection."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            db.close()
            # Verify connection is closed by attempting operation
            with pytest.raises(sqlite3.ProgrammingError):
                db.connection.execute("SELECT COUNT(*) FROM memories")

    def test_save_error_handling(self, temp_db):
        """Test error handling in save operation."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            # Close connection to cause error
            db.connection.close()
            
            with pytest.raises(Exception):
                db.save("Test memory")

    def test_get_all_error_handling(self, temp_db):
        """Test error handling in get_all operation."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            # Close connection to cause error
            db.connection.close()
            
            with pytest.raises(Exception):
                db.get_all()

    def test_memory_content_preserved(self, temp_db):
        """Test that memory content is preserved exactly."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            
            # Test with various content types
            test_content = "Test with 日本語 and தமிழ் and emoji 🎉"
            db.save(test_content)
            
            memories = db.get_all()
            assert len(memories) == 1
            assert memories[0][1] == test_content
            db.close()

    def test_memory_ordering(self, temp_db):
        """Test that memories are ordered by most recent first."""
        with patch("memory.database.DB_PATH", temp_db):
            db = MemoryDatabase()
            db.save("First")
            db.save("Second")
            db.save("Third")
            
            memories = db.get_all()
            # Should be in reverse order (DESC)
            assert memories[0][1] == "Third"
            assert memories[1][1] == "Second"
            assert memories[2][1] == "First"
            db.close()
