import unittest
from datetime import datetime, timedelta
from memory_system import MemoryManager, MemoryLevel, MemoryType, Memory
from memory_system.config import LLMConfig, DatabaseConfig

class MemoryRetentionTests(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.llm_config = LLMConfig(provider="openai")
        self.db_config = DatabaseConfig(provider="postgresql")
        self.memory_manager = MemoryManager(
            llm_config=self.llm_config,
            db_config=self.db_config
        )
        
    def test_basic_memory_retention(self):
        """Test basic memory storage and retrieval."""
        # Add a memory
        memory = self.memory_manager.add_experience(
            content="Important meeting about project X",
            level=MemoryLevel.TEAM,
            tags=["meeting", "project-x"],
            metadata={"date": "2024-01-01", "participants": ["Alice", "Bob"]}
        )
        
        # Query the memory
        query = MemoryQuery(
            content="project X meeting",
            level=MemoryLevel.TEAM,
            max_results=1
        )
        results = self.memory_manager.query_memories(query)
        
        # Verify retrieval
        self.assertEqual(len(results.retrieved_memories), 1)
        self.assertEqual(results.retrieved_memories[0].content, memory.content)
        
    def test_long_term_retention(self):
        """Test retention of memories over extended periods."""
        # Add memories with different timestamps
        old_memory = Memory(
            content="Old project meeting",
            level=MemoryLevel.TEAM,
            timestamp=datetime.now() - timedelta(days=60),
            tags=["meeting", "old-project"]
        )
        
        recent_memory = Memory(
            content="Recent project meeting",
            level=MemoryLevel.TEAM,
            timestamp=datetime.now() - timedelta(days=1),
            tags=["meeting", "new-project"]
        )
        
        self.memory_manager.add_experience(old_memory)
        self.memory_manager.add_experience(recent_memory)
        
        # Test memory cleanup
        self.memory_manager.cleanup_memories(threshold_days=30)
        
        # Query memories
        query = MemoryQuery(content="project meeting", max_results=10)
        results = self.memory_manager.query_memories(query)
        
        # Verify only recent memory is retained
        self.assertEqual(len(results.retrieved_memories), 1)
        self.assertEqual(results.retrieved_memories[0].content, recent_memory.content)
        
    def test_memory_relevance_update(self):
        """Test updating memory relevance scores."""
        # Add a memory
        memory = self.memory_manager.add_experience(
            content="Important technical decision",
            level=MemoryLevel.ORGANIZATION,
            tags=["technical", "decision"]
        )
        
        # Update relevance
        self.memory_manager.update_memory_relevance(memory.id, 0.5)
        
        # Query memory
        query = MemoryQuery(content="technical decision")
        results = self.memory_manager.query_memories(query)
        
        # Verify updated relevance
        self.assertGreaterEqual(results.retrieved_memories[0].relevance_score, 0.5)
        
    def test_memory_access_patterns(self):
        """Test memory access patterns and statistics."""
        # Add memories
        memory1 = self.memory_manager.add_experience(
            content="Frequently accessed memory",
            level=MemoryLevel.TEAM
        )
        
        memory2 = self.memory_manager.add_experience(
            content="Rarely accessed memory",
            level=MemoryLevel.TEAM
        )
        
        # Simulate access patterns
        for _ in range(10):
            query = MemoryQuery(content="frequently accessed")
            self.memory_manager.query_memories(query)
            
        # Get memory statistics
        stats = self.memory_manager.get_statistics()
        
        # Verify access counts
        self.assertGreater(
            memory1.access_count,
            memory2.access_count,
            "Frequently accessed memory should have higher access count"
        )
        
if __name__ == '__main__':
    unittest.main()
