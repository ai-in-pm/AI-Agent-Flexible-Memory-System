from memory_system import MemoryManager, MemoryLevel, MemoryQuery

def main():
    # Initialize the memory manager
    memory_manager = MemoryManager()
    
    # Add some sample memories
    print("Adding memories...")
    
    # Team level memories
    memory_manager.add_experience(
        content="Team meeting: Discussed new AI feature requirements. Key points: improved response time, better context handling",
        level=MemoryLevel.TEAM,
        tags=["meeting", "requirements", "AI"],
        metadata={"project": "AI Enhancement", "participants": ["Alice", "Bob", "Charlie"]}
    )
    
    memory_manager.add_experience(
        content="Technical review of current AI system performance metrics. Average response time: 200ms",
        level=MemoryLevel.TEAM,
        tags=["technical", "performance", "AI"],
        metadata={"project": "AI Enhancement", "metrics": {"response_time": 200}}
    )
    
    # Organizational level memory
    memory_manager.add_experience(
        content="Department-wide AI strategy meeting: Focus on scalability and reliability for next quarter",
        level=MemoryLevel.ORGANIZATION,
        tags=["strategy", "planning", "AI"],
        metadata={"department": "Engineering", "quarter": "Q1 2024"}
    )
    
    # Enterprise level memory
    memory_manager.add_experience(
        content="Company-wide announcement: New AI infrastructure investment approved for global deployment",
        level=MemoryLevel.ENTERPRISE,
        tags=["announcement", "infrastructure", "AI"],
        metadata={"impact": "global", "budget": "approved"}
    )
    
    # Query memories about AI and performance
    print("\nQuerying memories about AI performance...")
    query = MemoryQuery(
        content="AI system performance and requirements",
        max_results=3
    )
    
    analysis = memory_manager.query_memories(query)
    
    # Display results
    print("\nRetrieved Memories:")
    for memory, similarity in zip(analysis.retrieved_memories, analysis.similarities):
        print(f"\nMemory: {memory.content}")
        print(f"Level: {memory.level}")
        print(f"Similarity Score: {similarity:.2f}")
        print(f"Tags: {memory.tags}")
        print("---")
    
    print("\nInsights:")
    for insight in analysis.insights:
        print(f"- {insight}")
    
    print("\nRecommendations:")
    for recommendation in analysis.recommendations:
        print(f"- {recommendation}")
    
    # Get system statistics
    print("\nMemory System Statistics:")
    stats = memory_manager.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
