import unittest
from memory_system import MemoryManager, MemoryLevel, MemoryType, Memory, MemoryQuery
from memory_system.config import LLMConfig, DatabaseConfig
import json

class LLMIntegrationTests(unittest.TestCase):
    def setUp(self):
        """Set up test environment with different LLM providers."""
        self.llm_configs = {
            "openai": LLMConfig(
                provider="openai",
                model="gpt-4-turbo-preview",
                temperature=0.7
            ),
            "anthropic": LLMConfig(
                provider="anthropic",
                model="claude-3-opus-20240229",
                temperature=0.7
            ),
            "google": LLMConfig(
                provider="google",
                model="gemini-pro",
                temperature=0.7
            )
        }
        
        self.db_config = DatabaseConfig(provider="postgresql")
        self.memory_managers = {
            provider: MemoryManager(config, self.db_config)
            for provider, config in self.llm_configs.items()
        }
        
    def test_cross_provider_memory_analysis(self):
        """Test memory analysis across different LLM providers."""
        # Add same memory to all providers
        test_memory = {
            "content": "Important technical decision: Chose to use PostgreSQL for its ACID compliance",
            "level": MemoryLevel.ORGANIZATION,
            "tags": ["technical", "database", "decision"],
            "metadata": {
                "impact": "high",
                "stakeholders": ["engineering", "operations"]
            }
        }
        
        analysis_results = {}
        
        for provider, manager in self.memory_managers.items():
            # Add memory
            memory = manager.add_experience(**test_memory)
            
            # Query and analyze
            query = MemoryQuery(
                content="database decision rationale",
                level=MemoryLevel.ORGANIZATION
            )
            
            analysis = manager.query_memories(query)
            analysis_results[provider] = {
                "insights": analysis.insights,
                "recommendations": analysis.recommendations
            }
            
        # Compare analysis quality
        self._compare_analysis_quality(analysis_results)
        
    def test_multi_modal_memory_handling(self):
        """Test handling of multi-modal memories across providers."""
        test_cases = [
            {
                "content": "Meeting screenshot shows architecture diagram",
                "level": MemoryLevel.TEAM,
                "metadata": {
                    "type": "image",
                    "format": "png",
                    "dimensions": "1920x1080"
                }
            },
            {
                "content": "Voice memo from architecture review",
                "level": MemoryLevel.TEAM,
                "metadata": {
                    "type": "audio",
                    "format": "mp3",
                    "duration": "120"
                }
            }
        ]
        
        for provider, manager in self.memory_managers.items():
            for test_case in test_cases:
                # Add multi-modal memory
                memory = manager.add_experience(**test_case)
                
                # Query with modal-specific parameters
                query = MemoryQuery(
                    content=test_case["content"],
                    metadata={"type": test_case["metadata"]["type"]}
                )
                
                results = manager.query_memories(query)
                
                # Verify modal-specific handling
                self.assertEqual(
                    results.retrieved_memories[0].metadata["type"],
                    test_case["metadata"]["type"]
                )
                
    def test_memory_update_consistency(self):
        """Test consistency of memory updates across providers."""
        test_memory = {
            "content": "Initial project requirements",
            "level": MemoryLevel.TEAM,
            "tags": ["requirements", "initial"]
        }
        
        update_content = "Updated project requirements with new security features"
        
        for provider, manager in self.memory_managers.items():
            # Add initial memory
            memory = manager.add_experience(**test_memory)
            
            # Update memory
            updated_memory = manager.add_experience(
                content=update_content,
                level=MemoryLevel.TEAM,
                tags=["requirements", "security"],
                metadata={"previous_version": memory.id}
            )
            
            # Query for requirements
            query = MemoryQuery(content="project requirements")
            results = manager.query_memories(query)
            
            # Verify update handling
            self.assertEqual(
                results.retrieved_memories[0].content,
                update_content,
                f"Provider {provider} failed to prioritize updated content"
            )
            
    def test_cross_context_memory_retrieval(self):
        """Test retrieval of memories across different contexts."""
        contexts = [
            {
                "content": "Technical design discussion",
                "level": MemoryLevel.TEAM,
                "tags": ["technical", "design"]
            },
            {
                "content": "Project timeline planning",
                "level": MemoryLevel.ORGANIZATION,
                "tags": ["planning", "timeline"]
            },
            {
                "content": "Budget allocation meeting",
                "level": MemoryLevel.ENTERPRISE,
                "tags": ["finance", "planning"]
            }
        ]
        
        for provider, manager in self.memory_managers.items():
            # Add memories in different contexts
            for context in contexts:
                manager.add_experience(**context)
                
            # Query across contexts
            query = MemoryQuery(
                content="project planning aspects",
                max_results=10
            )
            
            results = manager.query_memories(query)
            
            # Verify cross-context retrieval
            self.assertGreaterEqual(
                len(results.retrieved_memories),
                2,
                f"Provider {provider} failed to retrieve cross-context memories"
            )
            
    def _compare_analysis_quality(self, analysis_results):
        """Compare quality of analysis across providers."""
        # Implement custom metrics for comparing analysis quality
        quality_scores = {}
        
        for provider, results in analysis_results.items():
            # Score based on number of insights
            insight_score = len(results["insights"]) * 0.5
            
            # Score based on number of recommendations
            recommendation_score = len(results["recommendations"]) * 0.5
            
            # Score based on content specificity (custom implementation)
            specificity_score = self._calculate_specificity(results)
            
            quality_scores[provider] = {
                "total_score": insight_score + recommendation_score + specificity_score,
                "breakdown": {
                    "insights": insight_score,
                    "recommendations": recommendation_score,
                    "specificity": specificity_score
                }
            }
            
        return quality_scores
        
    def _calculate_specificity(self, results):
        """Calculate specificity score for analysis results."""
        # Implement custom specificity calculation
        # This is a simplified example
        specificity_score = 0
        
        # Check for specific technical terms
        technical_terms = ["database", "PostgreSQL", "ACID", "compliance"]
        
        for insight in results["insights"]:
            specificity_score += sum(term.lower() in insight.lower() 
                                   for term in technical_terms) * 0.2
            
        for recommendation in results["recommendations"]:
            specificity_score += sum(term.lower() in recommendation.lower() 
                                   for term in technical_terms) * 0.2
            
        return min(specificity_score, 1.0)  # Normalize to max of 1.0
        
if __name__ == '__main__':
    unittest.main()
