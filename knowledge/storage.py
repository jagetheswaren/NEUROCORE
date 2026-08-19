import sqlite3
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("knowledge.storage")

class KnowledgeDatabase:
    """
    SQLite persistent storage for NEUROCORE Knowledge Base.
    Stores document metadata, text chunks, and embedding vectors.
    """
    def __init__(self, db_path: str = "data/knowledge.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT,
                    chunk_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT,
                    vector_json TEXT,
                    FOREIGN KEY (doc_id) REFERENCES documents (doc_id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            logger.info(f"KnowledgeDatabase initialized at {self.db_path}")

    def save_document(self, doc_id: str, filename: str, file_type: str, chunks: List[Dict[str, Any]], vectors: List[List[float]]):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Insert or replace document manifest
            cursor.execute("""
                INSERT OR REPLACE INTO documents (doc_id, filename, file_type, chunk_count, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, filename, file_type, len(chunks), datetime.now().isoformat()))

            # Delete any existing chunks for this doc_id
            cursor.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))

            # Insert chunks with vectors
            for i, chunk in enumerate(chunks):
                vec_json = json.dumps(vectors[i]) if i < len(vectors) else "[]"
                meta_json = json.dumps({
                    "source": chunk.get("source", filename),
                    "chunk_index": chunk.get("chunk_index", i),
                    "start_word": chunk.get("start_word", 0),
                    "end_word": chunk.get("end_word", 0)
                })

                cursor.execute("""
                    INSERT INTO chunks (doc_id, chunk_index, content, metadata_json, vector_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (doc_id, i, chunk["content"], meta_json, vec_json))

            conn.commit()
            logger.info(f"Saved document {doc_id} ('{filename}') with {len(chunks)} chunks to Knowledge Database.")

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.doc_id, c.chunk_index, c.content, c.metadata_json, c.vector_json, d.filename
                FROM chunks c
                JOIN documents d ON c.doc_id = d.doc_id
            """)
            rows = cursor.fetchall()
            
            results = []
            for r in rows:
                results.append({
                    "id": r[0],
                    "doc_id": r[1],
                    "chunk_index": r[2],
                    "content": r[3],
                    "metadata": json.loads(r[4]) if r[4] else {},
                    "vector": json.loads(r[5]) if r[5] else [],
                    "filename": r[6]
                })
            return results

    def list_documents(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doc_id, filename, file_type, chunk_count, created_at FROM documents ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [
                {
                    "doc_id": r[0],
                    "filename": r[1],
                    "file_type": r[2],
                    "chunk_count": r[3],
                    "created_at": r[4]
                }
                for r in rows
            ]

    def delete_document(self, doc_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
            cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
            conn.commit()
            return cursor.rowcount > 0
