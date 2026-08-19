import logging
from memory.embeddings import EmbeddingModel

logger = logging.getLogger("memory.vector_db")

class LocalVectorDB:
    """
    In-memory vector database supporting cosine similarity indexing & retrieval.
    """
    def __init__(self, dim=128):
        self.embedding_model = EmbeddingModel(vector_dim=dim)
        self.documents = []
        self.vectors = []

    def add(self, doc_id: str, content: str, metadata: dict = None):
        vec = self.embedding_model.encode(content)
        self.documents.append({
            "id": doc_id,
            "content": content,
            "metadata": metadata or {}
        })
        self.vectors.append(vec)
        logger.info(f"Added document {doc_id} to vector DB.")

    def search(self, query: str, top_k: int = 3) -> list:
        if not self.vectors:
            return []

        q_vec = self.embedding_model.encode(query)
        scores = []

        for idx, doc_vec in enumerate(self.vectors):
            dot_product = sum(a * b for a, b in zip(q_vec, doc_vec))
            scores.append((dot_product, self.documents[idx]))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [{"score": score, "document": doc} for score, doc in scores[:top_k]]
