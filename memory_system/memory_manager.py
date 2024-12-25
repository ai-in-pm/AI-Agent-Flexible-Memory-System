"""
Memory manager module.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from .models import Memory, MemoryLevel, MemoryType, MemoryQuery
from .memory_store import MemoryStore
from .embeddings import EmbeddingGenerator
from .config import LLMConfig, DatabaseConfig

class MemoryManager:
    """Manage memory operations."""
    
    def __init__(self, llm_config: LLMConfig, db_config: DatabaseConfig):
        """Initialize memory manager."""
        self.llm_config = llm_config
        self.db_config = db_config
        self.memory_store = MemoryStore(db_config)
        self.embedding_generator = EmbeddingGenerator(llm_config)
    
    def add_experience(
        self,
        content: str,
        level: MemoryLevel,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """Add a new experience memory."""
        if memory_type is None:
            memory_type = MemoryType.EXPERIENCE
        
        if metadata is None:
            metadata = {}
            
        if tags is None:
            tags = []
            
        memory = Memory(
            id=str(uuid.uuid4()),
            content=content,
            embedding=self.embedding_generator.generate(content),
            level=level,
            memory_type=memory_type,
            timestamp=datetime.now(),
            metadata=metadata,
            relevance_score=1.0,
            access_count=0,
            last_accessed=None,
            tags=tags
        )
        
        self.memory_store.store_memory(memory)
        return memory
    
    def search_memories(self, query: MemoryQuery) -> List[Memory]:
        """Search for memories based on query."""
        # Get embeddings for query content
        query_embedding = self.embedding_generator.generate(query.content)
        
        # Search memory store
        memories = self.memory_store.search_memories(
            query_embedding=query_embedding,
            level=query.level,
            memory_type=query.memory_type,
            min_relevance=query.min_relevance,
            max_results=query.max_results,
            tags=query.tags,
            metadata_filters=query.metadata_filters
        )
        
        return memories
    
    def update_memory(self, memory: Memory) -> bool:
        """Update an existing memory."""
        try:
            self.memory_store.update_memory(memory)
            return True
        except Exception as e:
            print(f"Error updating memory: {str(e)}")
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        try:
            self.memory_store.delete_memory(memory_id)
            return True
        except Exception as e:
            print(f"Error deleting memory: {str(e)}")
            return False
