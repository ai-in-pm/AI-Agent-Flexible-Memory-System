"""
Models for memory system.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import numpy as np

class MemoryLevel(str, Enum):
    """Memory level options."""
    INDIVIDUAL = "individual"
    TEAM = "team"
    ORGANIZATION = "organization"

class MemoryType(str, Enum):
    """Memory type options."""
    EXPERIENCE = "experience"
    KNOWLEDGE = "knowledge"
    INSIGHT = "insight"
    SKILL = "skill"

class Memory:
    """Memory model."""
    
    def __init__(
        self,
        id: str,
        content: str,
        embedding: np.ndarray,
        level: MemoryLevel,
        memory_type: MemoryType,
        timestamp: datetime,
        metadata: Optional[Dict[str, Any]] = None,
        relevance_score: float = 1.0,
        access_count: int = 0,
        last_accessed: Optional[datetime] = None,
        tags: Optional[List[str]] = None
    ):
        """Initialize memory."""
        self.id = id
        self.content = content
        self.embedding = embedding
        self.level = level
        self.memory_type = memory_type
        self.timestamp = timestamp
        self.metadata = metadata or {}
        self.relevance_score = relevance_score
        self.access_count = access_count
        self.last_accessed = last_accessed
        self.tags = tags or []

class MemoryQuery:
    """Memory query model."""
    
    def __init__(
        self,
        content: str,
        level: Optional[MemoryLevel] = None,
        memory_type: Optional[MemoryType] = None,
        min_relevance: float = 0.0,
        max_results: int = 10,
        tags: Optional[List[str]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None
    ):
        """Initialize memory query."""
        self.content = content
        self.level = level
        self.memory_type = memory_type
        self.min_relevance = min_relevance
        self.max_results = max_results
        self.tags = tags or []
        self.metadata_filters = metadata_filters or {}
