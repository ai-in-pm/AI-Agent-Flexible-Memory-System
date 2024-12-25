"""
Basic Memory Operations Demonstration
This script demonstrates the core functionality of the memory system.
"""

import sys
import os
import time
from datetime import datetime
from memory_system import MemoryManager, MemoryLevel, MemoryType, Memory, MemoryQuery
from memory_system.config import LLMConfig, DatabaseConfig, DatabaseProvider

def setup_memory_system():
    """Initialize the memory system with basic configuration."""
    llm_config = LLMConfig(
        provider="openai",
        api_key="dummy-key",
        additional_config={
            "temperature": 0.7,
            "model": "gpt-4-turbo-preview"
        }
    )
    
    db_config = DatabaseConfig(
        provider=DatabaseProvider.POSTGRESQL,
        host="localhost",
        port=5433,
        database="memory_system_demo",
        username="memory_system",
        password="memory_system_pass"
    )
    
    return MemoryManager(llm_config=llm_config, db_config=db_config)

def demonstrate_basic_operations():
    """Demonstrate basic memory operations with timing and results."""
    print("\n=== Basic Memory Operations Demo ===\n")
    
    memory_manager = setup_memory_system()
    results = {"success": 0, "total": 0}
    
    def log_operation(operation, success):
        """Log operation result with timestamp."""
        status = "Success" if success else "Failed"
        results["total"] += 1
        if success:
            results["success"] += 1
        print(f"{status} {datetime.now().isoformat()}: {operation}")
    
    # 1. Create memories
    try:
        print("\n1. Creating Memories...")
        memories = [
            {
                "content": "Team meeting about project roadmap",
                "level": MemoryLevel.TEAM,
                "memory_type": MemoryType.EXPERIENCE,
                "tags": ["meeting", "roadmap", "planning"],
                "metadata": {"participants": ["Alice", "Bob", "Charlie"]}
            },
            {
                "content": "Code review best practices document",
                "level": MemoryLevel.ORGANIZATION,
                "memory_type": MemoryType.KNOWLEDGE,
                "tags": ["code-review", "documentation", "best-practices"],
                "metadata": {"author": "DevOps Team", "version": "1.0"}
            }
        ]
        
        created_memories = []
        for memory_data in memories:
            memory = memory_manager.add_experience(
                content=memory_data["content"],
                level=memory_data["level"],
                memory_type=memory_data["memory_type"],
                tags=memory_data["tags"],
                metadata=memory_data["metadata"]
            )
            created_memories.append(memory)
            log_operation(f"Created memory: {memory.id}", True)
            
        # 2. Query memories
        print("\n2. Querying Memories...")
        query = MemoryQuery(
            content="project planning meeting",
            level=MemoryLevel.TEAM,
            tags=["meeting"],
            max_results=5
        )
        
        found_memories = memory_manager.search_memories(query)
        log_operation(f"Found {len(found_memories)} memories", True)
        
        # 3. Update memory
        if found_memories:
            print("\n3. Updating Memory...")
            memory_to_update = found_memories[0]
            memory_to_update.metadata["updated"] = True
            memory_to_update.tags.append("updated")
            success = memory_manager.update_memory(memory_to_update)
            log_operation(f"Updated memory: {memory_to_update.id}", success)
        
        # 4. Delete memory
        if len(created_memories) > 1:
            print("\n4. Deleting Memory...")
            memory_to_delete = created_memories[1]
            success = memory_manager.delete_memory(memory_to_delete.id)
            log_operation(f"Deleted memory: {memory_to_delete.id}", success)
            
        return results["success"] == results["total"]
        
    except Exception as e:
        print(f"Error: Basic Operations Demo failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = demonstrate_basic_operations()
    sys.exit(0 if success else 1)
