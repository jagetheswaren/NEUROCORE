import os
import shutil
import tempfile
import unittest
from pathlib import Path
from knowledge.ingestion.parser import DocumentParser
from knowledge.storage import KnowledgeDatabase
from knowledge.retrieval import KnowledgeRetriever

class TestKnowledgeEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_knowledge.db")
        
        self.sample_file = os.path.join(self.temp_dir, "sample_notes.txt")
        content = (
            "Java inheritance allows a class to inherit properties and methods from another class. "
            "The keyword used for inheritance in Java is extends. "
            "Single inheritance, multilevel inheritance, and hierarchical inheritance are supported. "
            "Multiple inheritance using classes is not supported in Java to avoid ambiguity."
        )
        with open(self.sample_file, "w", encoding="utf-8") as f:
            f.write(content)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_document_parser(self):
        parser = DocumentParser(chunk_size=20, overlap=5)
        chunks = parser.parse_file(self.sample_file)
        
        self.assertGreater(len(chunks), 0)
        self.assertEqual(chunks[0]["source"], "sample_notes.txt")
        self.assertIn("inheritance", chunks[0]["content"].lower())

    def test_knowledge_database(self):
        db = KnowledgeDatabase(db_path=self.db_path)
        
        chunks = [
            {"content": "Chunk 1 content about Python programming.", "source": "test.txt", "chunk_index": 0},
            {"content": "Chunk 2 content about FastAPI endpoints.", "source": "test.txt", "chunk_index": 1}
        ]
        vectors = [[0.1] * 128, [0.2] * 128]
        
        db.save_document("doc_001", "test.txt", ".txt", chunks, vectors)
        
        docs = db.list_documents()
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["doc_id"], "doc_001")
        self.assertEqual(docs[0]["chunk_count"], 2)
        
        all_chunks = db.get_all_chunks()
        self.assertEqual(len(all_chunks), 2)
        self.assertEqual(all_chunks[0]["content"], "Chunk 1 content about Python programming.")
        
        # Test delete
        deleted = db.delete_document("doc_001")
        self.assertTrue(deleted)
        self.assertEqual(len(db.list_documents()), 0)

    def test_knowledge_retriever(self):
        retriever = KnowledgeRetriever(db_path=self.db_path)
        
        # Test file ingestion
        ingest_res = retriever.ingest_file(self.sample_file)
        self.assertEqual(ingest_res["status"], "indexed")
        self.assertGreater(ingest_res["chunk_count"], 0)
        
        # Test search
        results = retriever.search("Java inheritance extends keyword", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("inheritance", results[0]["content"].lower())
        
        # Test format RAG context
        rag_context = retriever.format_rag_context("Java inheritance")
        self.assertIn("Relevant Local Knowledge", rag_context)
        self.assertIn("sample_notes.txt", rag_context)
        
        # Test text ingestion
        text_res = retriever.ingest_text("FastAPI provides automatic OpenAPI documentation at /docs.", filename="fastapi.txt")
        self.assertEqual(text_res["status"], "indexed")
        self.assertEqual(len(retriever.list_documents()), 2)

if __name__ == "__main__":
    unittest.main()
