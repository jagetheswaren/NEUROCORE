import logging
import math
import hashlib

logger = logging.getLogger("memory.embeddings")

class EmbeddingModel:
    """
    Local embedding generator using deterministic feature hashing.
    Enables zero-dependency local semantic vector search.
    """
    def __init__(self, vector_dim=128):
        self.dim = vector_dim

    def encode(self, text: str) -> list:
        words = text.lower().split()
        vector = [0.0] * self.dim

        for word in words:
            # Deterministic feature hash
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            index = h % self.dim
            val = (h % 100) / 100.0
            vector[index] += val

        # Normalize L2 norm
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector
