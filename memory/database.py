import logging
import sqlite3
from pathlib import Path


logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "brain.db"


class MemoryDatabase:

    def __init__(self):
        """Initialize memory database with error handling."""
        try:
            self.connection = sqlite3.connect(DB_PATH)
            logger.info(f"Connected to memory database: {DB_PATH}")
            self._create_tables()
        except sqlite3.Error as e:
            error_msg = f"Failed to initialize database: {str(e)}"
            logger.error(error_msg)
            raise

    def _create_tables(self):
        """Create required database tables with error handling."""
        try:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()
            logger.debug("Memory tables created/verified successfully")

        except sqlite3.Error as e:
            error_msg = f"Failed to create database tables: {str(e)}"
            logger.error(error_msg)
            raise

    def save(self, content: str, category: str = "general"):
        """Save a memory to the database with error handling."""
        try:
            self.connection.execute(
                """
                INSERT INTO memories (content, category)
                VALUES (?, ?)
                """,
                (content, category)
            )

            self.connection.commit()
            logger.debug(f"Saved memory: category={category}, length={len(content)}")

        except sqlite3.Error as e:
            error_msg = f"Failed to save memory: {str(e)}"
            logger.error(error_msg)
            raise

    def get_all(self):
        """Retrieve all memories with error handling."""
        try:
            cursor = self.connection.execute(
                """
                SELECT id, content, category, created_at
                FROM memories
                ORDER BY id DESC
                """
            )

            memories = cursor.fetchall()
            logger.debug(f"Retrieved {len(memories)} memories from database")
            return memories

        except sqlite3.Error as e:
            error_msg = f"Failed to retrieve memories: {str(e)}"
            logger.error(error_msg)
            raise

    def close(self):
        """Close database connection with error handling."""
        try:
            if self.connection:
                self.connection.close()
                logger.info("Database connection closed successfully")
        except sqlite3.Error as e:
            error_msg = f"Error closing database connection: {str(e)}"
            logger.error(error_msg)
            raise