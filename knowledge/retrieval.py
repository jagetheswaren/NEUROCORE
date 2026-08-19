import logging
import uuid
from typing import List, Dict, Any, Optional
from knowledge.ingestion.parser import DocumentParser
from knowledge.storage import KnowledgeDatabase
from memory.embeddings import EmbeddingModel

logger = logging.getLogger("knowledge.retrieval")

class KnowledgeRetriever:
    """
    RAG Retrieval Engine for NEUROCORE.
    Handles document ingestion, vector encoding, semantic search, and prompt context synthesis.
    """
    def __init__(self, db_path: str = "data/knowledge.db"):
        self.parser = DocumentParser()
        self.db = KnowledgeDatabase(db_path=db_path)
        self.embedding_model = EmbeddingModel(vector_dim=128)

    def ingest_file(self, file_path: str, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Parse a local document, calculate vector embeddings, and save to database."""
        chunks = self.parser.parse_file(file_path)
        if not chunks:
            return {"doc_id": doc_id, "chunk_count": 0, "status": "empty"}

        filename = chunks[0]["source"]
        file_type = chunks[0]["file_type"]
        document_id = doc_id or f"doc_{uuid.uuid4().hex[:8]}"

        vectors = [self.embedding_model.encode(c["content"]) for c in chunks]
        self.db.save_document(document_id, filename, file_type, chunks, vectors)

        return {
            "doc_id": document_id,
            "filename": filename,
            "file_type": file_type,
            "chunk_count": len(chunks),
            "status": "indexed"
        }

    def ingest_text(self, text: str, filename: str = "raw_input.txt", doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Ingest raw text or code directly into the knowledge base."""
        chunks = self.parser.chunk_text(text, source=filename, file_type=".txt")
        if not chunks:
            return {"doc_id": doc_id, "chunk_count": 0, "status": "empty"}

        document_id = doc_id or f"doc_{uuid.uuid4().hex[:8]}"
        vectors = [self.embedding_model.encode(c["content"]) for c in chunks]
        self.db.save_document(document_id, filename, ".txt", chunks, vectors)

        return {
            "doc_id": document_id,
            "filename": filename,
            "file_type": ".txt",
            "chunk_count": len(chunks),
            "status": "indexed"
        }

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search knowledge base using hybrid vector similarity + keyword relevance."""
        all_chunks = self.db.get_all_chunks()
        if not all_chunks:
            return []

        q_vec = self.embedding_model.encode(query)
        q_words = set(query.lower().split())

        scored_chunks = []
        for item in all_chunks:
            vec = item.get("vector", [])
            content = item.get("content", "")
            
            # Cosine similarity score
            vec_score = 0.0
            if vec and len(vec) == len(q_vec):
                vec_score = sum(a * b for a, b in zip(q_vec, vec))

            # Keyword overlap score
            c_words = set(content.lower().split())
            overlap = len(q_words.intersection(c_words))
            kw_score = overlap / max(len(q_words), 1)

            # Combined hybrid score (70% vector, 30% keyword)
            final_score = (0.7 * vec_score) + (0.3 * kw_score)
            
            if final_score > 0.05:
                scored_chunks.append({
                    "score": round(final_score, 4),
                    "filename": item.get("filename"),
                    "doc_id": item.get("doc_id"),
                    "chunk_index": item.get("chunk_index"),
                    "content": content
                })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def format_rag_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve matching chunks and format into an explicit RAG context block for prompts."""
        results = self.search(query, top_k=top_k)
        if not results:
            return ""

        context_lines = ["Relevant Local Knowledge & Document Extracts:"]
        for res in results:
            context_lines.append(f"• [{res['filename']} - Fragment #{res['chunk_index']}]: {res['content']}")

        return "\n".join(context_lines)

    def list_documents(self) -> List[Dict[str, Any]]:
        return self.db.list_documents()

    def delete_document(self, doc_id: str) -> bool:
        return self.db.delete_document(doc_id)
