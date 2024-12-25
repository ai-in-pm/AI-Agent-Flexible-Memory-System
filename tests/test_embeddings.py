"""Test embedding functionality."""

import pytest
import numpy as np
from memory_system.embeddings import EmbeddingGenerator
from memory_system.config import LLMConfig

def test_embedding_generation():
    """Test generating embeddings."""
    llm_config = LLMConfig(
        provider="openai",
        api_key="test-key",
        additional_config={
            "temperature": 0.7,
            "model": "gpt-4-turbo-preview"
        }
    )
    
    generator = EmbeddingGenerator(llm_config)
    text = "Test text for embedding generation"
    embedding = generator.generate(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)
    assert all(0 <= x <= 1 for x in embedding)

def test_embedding_similarity():
    """Test embedding similarity calculation."""
    llm_config = LLMConfig(
        provider="openai",
        api_key="test-key",
        additional_config={
            "temperature": 0.7,
            "model": "gpt-4-turbo-preview"
        }
    )
    
    generator = EmbeddingGenerator(llm_config)
    text1 = "Test text for embedding generation"
    text2 = "Another test text for embedding"
    
    embedding1 = generator.generate(text1)
    embedding2 = generator.generate(text2)
    
    # Convert to numpy arrays for cosine similarity calculation
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Calculate cosine similarity
    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    assert 0 <= similarity <= 1
