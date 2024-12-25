import unittest
from datetime import datetime, timedelta
from memory_system import MemoryManager, MemoryLevel, MemoryType, Memory, MemoryQuery
from memory_system.config import LLMConfig, DatabaseConfig

class SpecificUseCaseTests(unittest.TestCase):
    def setUp(self):
        self.llm_config = LLMConfig(provider="openai")
        self.db_config = DatabaseConfig(provider="postgresql")
        self.memory_manager = MemoryManager(
            llm_config=self.llm_config,
            db_config=self.db_config
        )

    def test_code_review_memory(self):
        """Test memory system in code review scenarios."""
        # Add code review memories
        review_memories = [
            {
                "content": "Code review feedback: Implement proper error handling in auth module",
                "level": MemoryLevel.TEAM,
                "tags": ["code-review", "auth", "error-handling"],
                "metadata": {
                    "pull_request": "PR-123",
                    "reviewer": "senior_dev",
                    "priority": "high"
                }
            },
            {
                "content": "Code review pattern: Always use prepared statements for SQL queries",
                "level": MemoryLevel.ORGANIZATION,
                "tags": ["code-review", "sql", "security"],
                "metadata": {
                    "category": "best-practice",
                    "impact": "security"
                }
            }
        ]

        for memory_data in review_memories:
            self.memory_manager.add_experience(**memory_data)

        # Test retrieval of relevant code review patterns
        query = MemoryQuery(
            content="SQL security best practices from code reviews",
            level=MemoryLevel.ORGANIZATION
        )
        results = self.memory_manager.query_memories(query)

        self.assertTrue(
            any("SQL" in memory.content for memory in results.retrieved_memories),
            "Failed to retrieve SQL-related code review patterns"
        )

    def test_incident_response_memory(self):
        """Test memory system in incident response scenarios."""
        # Add incident-related memories
        incident_memories = [
            {
                "content": "Production incident: Database connection pool exhaustion",
                "level": MemoryLevel.ENTERPRISE,
                "tags": ["incident", "database", "production"],
                "metadata": {
                    "incident_id": "INC-456",
                    "severity": "high",
                    "resolution_time": "2h"
                }
            },
            {
                "content": "Incident resolution: Implemented connection pooling limits",
                "level": MemoryLevel.ENTERPRISE,
                "tags": ["incident", "resolution", "database"],
                "metadata": {
                    "incident_id": "INC-456",
                    "preventive_measure": True
                }
            }
        ]

        for memory_data in incident_memories:
            self.memory_manager.add_experience(**memory_data)

        # Test incident pattern recognition
        query = MemoryQuery(
            content="database connection issues resolution",
            level=MemoryLevel.ENTERPRISE,
            tags=["incident", "resolution"]
        )
        results = self.memory_manager.query_memories(query)

        self.assertTrue(
            any("connection pooling" in memory.content 
                for memory in results.retrieved_memories),
            "Failed to retrieve incident resolution pattern"
        )

    def test_architectural_decision_memory(self):
        """Test memory system for architectural decisions."""
        # Add architectural decision memories
        architecture_memories = [
            {
                "content": "ADR: Adopted microservices architecture for scalability",
                "level": MemoryLevel.ENTERPRISE,
                "tags": ["architecture", "ADR", "microservices"],
                "metadata": {
                    "decision_id": "ADR-789",
                    "status": "approved",
                    "impact": "high"
                }
            },
            {
                "content": "Architecture update: Implementing service mesh for observability",
                "level": MemoryLevel.ENTERPRISE,
                "tags": ["architecture", "service-mesh", "observability"],
                "metadata": {
                    "related_adr": "ADR-789",
                    "implementation_phase": "planning"
                }
            }
        ]

        for memory_data in architecture_memories:
            self.memory_manager.add_experience(**memory_data)

        # Test architectural decision retrieval
        query = MemoryQuery(
            content="microservices architecture decisions",
            level=MemoryLevel.ENTERPRISE,
            tags=["architecture"]
        )
        results = self.memory_manager.query_memories(query)

        self.assertTrue(
            any("microservices" in memory.content 
                for memory in results.retrieved_memories),
            "Failed to retrieve architectural decisions"
        )

    def test_team_knowledge_transfer(self):
        """Test memory system for team knowledge transfer."""
        # Add knowledge transfer memories
        knowledge_memories = [
            {
                "content": "Onboarding guide: Setup development environment",
                "level": MemoryLevel.TEAM,
                "tags": ["onboarding", "setup", "development"],
                "metadata": {
                    "category": "onboarding",
                    "last_updated": datetime.now().isoformat()
                }
            },
            {
                "content": "Team best practices: Code review checklist",
                "level": MemoryLevel.TEAM,
                "tags": ["best-practices", "code-review", "process"],
                "metadata": {
                    "category": "process",
                    "status": "active"
                }
            }
        ]

        for memory_data in knowledge_memories:
            self.memory_manager.add_experience(**memory_data)

        # Test knowledge retrieval for new team members
        query = MemoryQuery(
            content="development environment setup guide",
            level=MemoryLevel.TEAM,
            tags=["onboarding"]
        )
        results = self.memory_manager.query_memories(query)

        self.assertTrue(
            any("development environment" in memory.content 
                for memory in results.retrieved_memories),
            "Failed to retrieve onboarding information"
        )

    def test_project_planning_memory(self):
        """Test memory system for project planning scenarios."""
        # Add project planning memories
        planning_memories = [
            {
                "content": "Project estimation: User authentication module - 2 weeks",
                "level": MemoryLevel.TEAM,
                "tags": ["planning", "estimation", "auth"],
                "metadata": {
                    "project": "user-auth",
                    "confidence": "high"
                }
            },
            {
                "content": "Similar project completion: Auth module took 3 weeks",
                "level": MemoryLevel.ORGANIZATION,
                "tags": ["planning", "historical", "auth"],
                "metadata": {
                    "project": "previous-auth",
                    "actual_duration": "3 weeks"
                }
            }
        ]

        for memory_data in planning_memories:
            self.memory_manager.add_experience(**memory_data)

        # Test historical project data retrieval
        query = MemoryQuery(
            content="authentication module implementation time",
            tags=["planning", "auth"]
        )
        results = self.memory_manager.query_memories(query)

        self.assertEqual(
            len(results.retrieved_memories),
            2,
            "Failed to retrieve all relevant project planning memories"
        )

    def test_security_audit_memory(self):
        """Test memory system for security audit scenarios."""
        # Add security audit memories
        security_memories = [
            {
                "content": "Security audit finding: Weak password policy",
                "level": MemoryLevel.ENTERPRISE,
                "tags": ["security", "audit", "authentication"],
                "metadata": {
                    "severity": "high",
                    "compliance": "SOC2"
                }
            },
            {
                "content": "Security implementation: Enhanced password requirements",
                "level": MemoryLevel.ENTERPRISE,
                "tags": ["security", "implementation", "authentication"],
                "metadata": {
                    "status": "completed",
                    "verification": "passed"
                }
            }
        ]

        for memory_data in security_memories:
            self.memory_manager.add_experience(**memory_data)

        # Test security audit trail retrieval
        query = MemoryQuery(
            content="password policy changes",
            level=MemoryLevel.ENTERPRISE,
            tags=["security"]
        )
        results = self.memory_manager.query_memories(query)

        self.assertTrue(
            all(memory.metadata.get("severity") == "high" 
                or memory.metadata.get("status") == "completed"
                for memory in results.retrieved_memories),
            "Failed to retrieve complete security audit trail"
        )

if __name__ == '__main__':
    unittest.main()
