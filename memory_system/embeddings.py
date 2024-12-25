"""
Embedding generation module.
"""

import numpy as np
from typing import List

class EmbeddingGenerator:
    """Generate embeddings for text."""
    
    def __init__(self, llm_config):
        """Initialize embedding generator."""
        self.llm_config = llm_config
        self.embedding_size = 192  # Using a smaller size for demonstration
        np.random.seed(42)  # For reproducible test results
        
    def generate(self, text: str) -> List[float]:
        """Generate embedding for text."""
        # For demonstration purposes, generate random embeddings
        # In a real implementation, this would use the LLM provider's embedding API
        embedding = np.random.uniform(0, 1, self.embedding_size)  # Use uniform distribution between 0 and 1
        embedding = embedding / np.linalg.norm(embedding)  # Normalize to unit vector
        return embedding.tolist()  # Convert to list
