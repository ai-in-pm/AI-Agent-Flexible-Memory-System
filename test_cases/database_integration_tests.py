import unittest
from memory_system import MemoryManager, MemoryLevel, MemoryType, Memory, MemoryQuery
from memory_system.config import LLMConfig, DatabaseConfig
import numpy as np
from datetime import datetime, timedelta

class DatabaseIntegrationTests(unittest.TestCase):
    def setUp(self):
        """Set up test environment with different database providers."""
        self.llm_config = LLMConfig(provider="openai")
        self.db_configs = {
            "postgresql": DatabaseConfig(
                provider="postgresql",
                host="localhost",
                port=5432,
                database="memory_system_test"
            ),
            "mongodb": DatabaseConfig(
                provider="mongodb",
                host="localhost",
                port=27017,
                database="memory_system_test"
            ),
            "redis": DatabaseConfig(
                provider="redis",
                host="localhost",
                port=6379,
                database=0
            ),
            "elasticsearch": DatabaseConfig(
                provider="elasticsearch",
                host="localhost",
                port=9200
            )
        }
        
        self.memory_managers = {
            provider: MemoryManager(self.llm_config, config)
            for provider, config in self.db_configs.items()
        }
        
    def test_memory_persistence(self):
        """Test memory persistence across different databases."""
        test_memory = {
            "content": "Critical system architecture decision",
            "level": MemoryLevel.ORGANIZATION,
            "tags": ["architecture", "decision"],
            "metadata": {
                "impact": "high",
                "approved_by": "tech_board"
            }
        }
        
        for provider, manager in self.memory_managers.items():
            # Add memory
            memory = manager.add_experience(**test_memory)
            
            # Verify immediate retrieval
            query = MemoryQuery(content="architecture decision")
            results = manager.query_memories(query)
            
            self.assertEqual(
                len(results.retrieved_memories),
                1,
                f"Provider {provider} failed immediate retrieval"
            )
            
            # Simulate system restart by creating new manager
            new_manager = MemoryManager(
                self.llm_config,
                self.db_configs[provider]
            )
            
            # Verify persistence
            results = new_manager.query_memories(query)
            self.assertEqual(
                len(results.retrieved_memories),
                1,
                f"Provider {provider} failed persistence test"
            )
            
    def test_concurrent_access(self):
        """Test concurrent memory access patterns."""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def concurrent_operation(manager, operation, memory_data, results_queue):
            try:
                if operation == "write":
                    memory = manager.add_experience(**memory_data)
                    results_queue.put(("write", memory.id, None))
                elif operation == "read":
                    query = MemoryQuery(content=memory_data["content"])
                    results = manager.query_memories(query)
                    results_queue.put(("read", None, len(results.retrieved_memories)))
            except Exception as e:
                results_queue.put(("error", str(e), None))
                
        for provider, manager in self.memory_managers.items():
            threads = []
            
            # Create write operations
            for i in range(5):
                memory_data = {
                    "content": f"Concurrent test memory {i}",
                    "level": MemoryLevel.TEAM,
                    "tags": ["concurrent", f"test_{i}"]
                }
                
                thread = threading.Thread(
                    target=concurrent_operation,
                    args=(manager, "write", memory_data, results_queue)
                )
                threads.append(thread)
                
            # Create read operations
            for i in range(5):
                memory_data = {"content": "concurrent test"}
                thread = threading.Thread(
                    target=concurrent_operation,
                    args=(manager, "read", memory_data, results_queue)
                )
                threads.append(thread)
                
            # Run threads
            for thread in threads:
                thread.start()
                
            # Wait for completion
            for thread in threads:
                thread.join()
                
            # Analyze results
            results = []
            while not results_queue.empty():
                results.append(results_queue.get())
                
            # Verify operations
            write_count = sum(1 for r in results if r[0] == "write")
            read_count = sum(1 for r in results if r[0] == "read")
            error_count = sum(1 for r in results if r[0] == "error")
            
            self.assertEqual(write_count, 5, 
                           f"Provider {provider} failed write operations")
            self.assertEqual(read_count, 5, 
                           f"Provider {provider} failed read operations")
            self.assertEqual(error_count, 0, 
                           f"Provider {provider} had concurrent access errors")
            
    def test_large_scale_operations(self):
        """Test database performance with large-scale operations."""
        # Generate large dataset
        large_dataset = [
            {
                "content": f"Large scale test memory {i}",
                "level": MemoryLevel.TEAM,
                "tags": ["large_scale", f"test_{i}"],
                "metadata": {"index": i}
            }
            for i in range(1000)
        ]
        
        for provider, manager in self.memory_managers.items():
            # Measure insertion time
            start_time = datetime.now()
            
            for data in large_dataset:
                manager.add_experience(**data)
                
            insertion_time = (datetime.now() - start_time).total_seconds()
            
            # Measure query time
            start_time = datetime.now()
            query = MemoryQuery(
                content="large scale test",
                max_results=100
            )
            results = manager.query_memories(query)
            query_time = (datetime.now() - start_time).total_seconds()
            
            # Verify performance
            self.assertLess(
                insertion_time,
                60,
                f"Provider {provider} failed insertion performance test"
            )
            self.assertLess(
                query_time,
                5,
                f"Provider {provider} failed query performance test"
            )
            
    def test_data_integrity(self):
        """Test data integrity across database operations."""
        test_cases = [
            {
                "content": "Unicode test: 你好世界",
                "level": MemoryLevel.TEAM,
                "tags": ["unicode"]
            },
            {
                "content": "Special chars test: !@#$%^&*()",
                "level": MemoryLevel.TEAM,
                "tags": ["special_chars"]
            },
            {
                "content": "Large content test: " + "x" * 10000,
                "level": MemoryLevel.TEAM,
                "tags": ["large_content"]
            }
        ]
        
        for provider, manager in self.memory_managers.items():
            for test_case in test_cases:
                # Add memory
                memory = manager.add_experience(**test_case)
                
                # Retrieve and verify
                query = MemoryQuery(content=test_case["content"][:100])
                results = manager.query_memories(query)
                
                retrieved_memory = results.retrieved_memories[0]
                
                self.assertEqual(
                    retrieved_memory.content,
                    test_case["content"],
                    f"Provider {provider} failed content integrity test"
                )
                
    def test_backup_restore(self):
        """Test backup and restore operations."""
        test_memories = [
            {
                "content": f"Backup test memory {i}",
                "level": MemoryLevel.TEAM,
                "tags": ["backup", f"test_{i}"]
            }
            for i in range(10)
        ]
        
        for provider, manager in self.memory_managers.items():
            # Add test data
            for memory_data in test_memories:
                manager.add_experience(**memory_data)
                
            # Perform backup (implementation depends on provider)
            backup_data = self._backup_database(provider, manager)
            
            # Clear database
            self._clear_database(provider, manager)
            
            # Restore from backup
            self._restore_database(provider, manager, backup_data)
            
            # Verify restoration
            query = MemoryQuery(content="backup test")
            results = manager.query_memories(query)
            
            self.assertEqual(
                len(results.retrieved_memories),
                10,
                f"Provider {provider} failed backup/restore test"
            )
            
    def _backup_database(self, provider, manager):
        """Implement provider-specific backup logic."""
        # This is a placeholder - implement actual backup logic
        return None
        
    def _clear_database(self, provider, manager):
        """Implement provider-specific database clearing logic."""
        # This is a placeholder - implement actual clearing logic
        pass
        
    def _restore_database(self, provider, manager, backup_data):
        """Implement provider-specific restore logic."""
        # This is a placeholder - implement actual restore logic
        pass
        
if __name__ == '__main__':
    unittest.main()
