import unittest
import time
import numpy as np
from datetime import datetime, timedelta
from memory_system import MemoryManager, MemoryLevel, MemoryType, Memory, MemoryQuery
from memory_system.config import LLMConfig, DatabaseConfig
import psutil
import os

class PerformanceBenchmarkTests(unittest.TestCase):
    def setUp(self):
        """Initialize test environment with various configurations."""
        self.llm_configs = {
            "openai-basic": LLMConfig(
                provider="openai",
                model="gpt-3.5-turbo",
                temperature=0.7
            ),
            "openai-advanced": LLMConfig(
                provider="openai",
                model="gpt-4-turbo-preview",
                temperature=0.7
            ),
            "anthropic": LLMConfig(
                provider="anthropic",
                model="claude-3-opus-20240229",
                temperature=0.7
            )
        }
        
        self.db_configs = {
            "postgresql": DatabaseConfig(
                provider="postgresql",
                host="localhost",
                port=5432
            ),
            "mongodb": DatabaseConfig(
                provider="mongodb",
                host="localhost",
                port=27017
            )
        }
        
        self.memory_managers = {}
        for llm_name, llm_config in self.llm_configs.items():
            for db_name, db_config in self.db_configs.items():
                config_name = f"{llm_name}-{db_name}"
                self.memory_managers[config_name] = MemoryManager(
                    llm_config=llm_config,
                    db_config=db_config
                )

    def _measure_memory_usage(self):
        """Measure current memory usage of the process."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB

    def _generate_test_memories(self, count, size="small"):
        """Generate test memories of specified size."""
        content_sizes = {
            "small": 100,    # 100 chars
            "medium": 1000,  # 1KB
            "large": 10000   # 10KB
        }
        
        return [
            {
                "content": f"Test memory {i} " + "x" * content_sizes[size],
                "level": MemoryLevel.TEAM,
                "tags": [f"test_{i}", "benchmark"],
                "metadata": {"index": i}
            }
            for i in range(count)
        ]

    def test_insertion_performance(self):
        """Benchmark memory insertion performance."""
        test_sizes = [100, 1000, 10000]
        results = {}
        
        for config_name, manager in self.memory_managers.items():
            config_results = {}
            
            for size in test_sizes:
                memories = self._generate_test_memories(size)
                
                # Measure insertion time
                start_time = time.time()
                start_memory = self._measure_memory_usage()
                
                for memory in memories:
                    manager.add_experience(**memory)
                    
                end_time = time.time()
                end_memory = self._measure_memory_usage()
                
                config_results[size] = {
                    "time": end_time - start_time,
                    "memory_increase": end_memory - start_memory,
                    "rate": size / (end_time - start_time)
                }
                
            results[config_name] = config_results
            
        # Log results
        self._log_benchmark_results("Insertion Performance", results)

    def test_query_performance(self):
        """Benchmark memory query performance."""
        dataset_sizes = [100, 1000, 10000]
        query_complexities = {
            "simple": "test memory",
            "complex": "test memory with specific tags and metadata",
            "semantic": "find memories related to testing and benchmarking"
        }
        
        results = {}
        
        for config_name, manager in self.memory_managers.items():
            config_results = {}
            
            for size in dataset_sizes:
                # Prepare dataset
                memories = self._generate_test_memories(size)
                for memory in memories:
                    manager.add_experience(**memory)
                    
                complexity_results = {}
                
                for complexity, query_text in query_complexities.items():
                    query = MemoryQuery(
                        content=query_text,
                        max_results=min(size, 100)
                    )
                    
                    # Measure query time
                    start_time = time.time()
                    start_memory = self._measure_memory_usage()
                    
                    results = manager.query_memories(query)
                    
                    end_time = time.time()
                    end_memory = self._measure_memory_usage()
                    
                    complexity_results[complexity] = {
                        "time": end_time - start_time,
                        "memory_increase": end_memory - start_memory,
                        "results_count": len(results.retrieved_memories)
                    }
                    
                config_results[size] = complexity_results
                
            results[config_name] = config_results
            
        # Log results
        self._log_benchmark_results("Query Performance", results)

    def test_memory_scalability(self):
        """Test system scalability with increasing memory load."""
        memory_sizes = ["small", "medium", "large"]
        counts = [100, 1000]
        results = {}
        
        for config_name, manager in self.memory_managers.items():
            config_results = {}
            
            for size in memory_sizes:
                size_results = {}
                
                for count in counts:
                    memories = self._generate_test_memories(count, size)
                    
                    # Measure insertion
                    start_time = time.time()
                    start_memory = self._measure_memory_usage()
                    
                    for memory in memories:
                        manager.add_experience(**memory)
                        
                    # Measure query
                    query = MemoryQuery(
                        content="test memory",
                        max_results=min(count, 100)
                    )
                    query_results = manager.query_memories(query)
                    
                    end_time = time.time()
                    end_memory = self._measure_memory_usage()
                    
                    size_results[count] = {
                        "total_time": end_time - start_time,
                        "memory_usage": end_memory - start_memory,
                        "retrieved_count": len(query_results.retrieved_memories)
                    }
                    
                config_results[size] = size_results
                
            results[config_name] = config_results
            
        # Log results
        self._log_benchmark_results("Scalability Test", results)

    def test_concurrent_performance(self):
        """Test performance under concurrent operations."""
        import threading
        import queue
        
        thread_counts = [5, 10, 20]
        results = {}
        
        def worker(manager, operation, data, result_queue):
            try:
                start_time = time.time()
                if operation == "write":
                    memory = manager.add_experience(**data)
                    result_queue.put(("write", time.time() - start_time))
                else:  # read
                    query = MemoryQuery(content=data["content"])
                    results = manager.query_memories(query)
                    result_queue.put(("read", time.time() - start_time))
            except Exception as e:
                result_queue.put(("error", str(e)))
                
        for config_name, manager in self.memory_managers.items():
            config_results = {}
            
            for thread_count in thread_counts:
                threads = []
                result_queue = queue.Queue()
                
                # Create mixed read/write operations
                for i in range(thread_count):
                    operation = "write" if i % 2 == 0 else "read"
                    data = {
                        "content": f"Concurrent test memory {i}",
                        "level": MemoryLevel.TEAM,
                        "tags": ["concurrent", f"test_{i}"]
                    }
                    
                    thread = threading.Thread(
                        target=worker,
                        args=(manager, operation, data, result_queue)
                    )
                    threads.append(thread)
                    
                # Run threads
                start_time = time.time()
                for thread in threads:
                    thread.start()
                    
                for thread in threads:
                    thread.join()
                    
                total_time = time.time() - start_time
                
                # Analyze results
                operation_times = {"write": [], "read": [], "error": []}
                while not result_queue.empty():
                    op, time = result_queue.get()
                    operation_times[op].append(time)
                    
                config_results[thread_count] = {
                    "total_time": total_time,
                    "avg_write_time": np.mean(operation_times["write"]),
                    "avg_read_time": np.mean(operation_times["read"]),
                    "error_count": len(operation_times["error"])
                }
                
            results[config_name] = config_results
            
        # Log results
        self._log_benchmark_results("Concurrent Performance", results)

    def _log_benchmark_results(self, test_name, results):
        """Log benchmark results in a structured format."""
        print(f"\n=== {test_name} Results ===")
        
        for config_name, config_results in results.items():
            print(f"\nConfiguration: {config_name}")
            
            if isinstance(config_results, dict):
                for key, value in config_results.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for metric, metric_value in value.items():
                            print(f"    {metric}: {metric_value}")
                    else:
                        print(f"  {key}: {value}")
                        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"benchmark_results_{test_name.lower().replace(' ', '_')}_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"=== {test_name} Results ===\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
            
            for config_name, config_results in results.items():
                f.write(f"\nConfiguration: {config_name}\n")
                f.write(str(config_results))
                f.write("\n")

if __name__ == '__main__':
    unittest.main()
