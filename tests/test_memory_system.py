"""Test memory system functionality."""

import pytest
from datetime import datetime
from memory_system import (
    MemoryManager,
    MemoryLevel,
    MemoryType,
    Memory,
    MemoryQuery,
    DatabaseConfig,
    LLMConfig,
    DatabaseProvider
)

@pytest.fixture
def memory_manager():
    """Create a memory manager for testing."""
    llm_config = LLMConfig(
        provider="openai",
        api_key="test-key",
        additional_config={
            "temperature": 0.7,
            "model": "gpt-4-turbo-preview"
        }
    )
    
    db_config = DatabaseConfig(
        provider=DatabaseProvider.POSTGRESQL,
        host="localhost",
        port=5433,
        database="memory_system_demo",  # Use the same database as the demo
        username="memory_system",
        password="memory_system_pass"
    )
    
    return MemoryManager(llm_config=llm_config, db_config=db_config)

def test_memory_creation():
    """Test creating a new memory."""
    memory = Memory(
        id="test-id",
        content="Test memory content",
        embedding=[0.1, 0.2, 0.3],
        level=MemoryLevel.TEAM,
        memory_type=MemoryType.EXPERIENCE,
        timestamp=datetime.now(),
        metadata={"test": "metadata"},
        relevance_score=1.0,
        access_count=0,
        last_accessed=None,
        tags=["test", "memory"]
    )
    
    assert memory.id == "test-id"
    assert memory.content == "Test memory content"
    assert memory.level == MemoryLevel.TEAM
    assert memory.memory_type == MemoryType.EXPERIENCE
    assert memory.metadata == {"test": "metadata"}
    assert memory.tags == ["test", "memory"]

def test_memory_query_creation():
    """Test creating a memory query."""
    query = MemoryQuery(
        content="Test query",
        level=MemoryLevel.TEAM,
        memory_type=MemoryType.EXPERIENCE,
        min_relevance=0.5,
        max_results=10,
        tags=["test"],
        metadata_filters={"test": "filter"}
    )
    
    assert query.content == "Test query"
    assert query.level == MemoryLevel.TEAM
    assert query.memory_type == MemoryType.EXPERIENCE
    assert query.min_relevance == 0.5
    assert query.max_results == 10
    assert query.tags == ["test"]
    assert query.metadata_filters == {"test": "filter"}

def test_memory_manager_initialization(memory_manager):
    """Test memory manager initialization."""
    assert memory_manager is not None
    assert memory_manager.llm_config is not None
    assert memory_manager.db_config is not None
    assert memory_manager.memory_store is not None
    assert memory_manager.embedding_generator is not None
