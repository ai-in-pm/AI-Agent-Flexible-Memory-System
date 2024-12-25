"""
Configuration module for memory system.
"""

from enum import Enum
from typing import Dict, Any, Optional

class DatabaseProvider(Enum):
    """Database provider options."""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"

class LLMConfig:
    """LLM configuration."""
    
    def __init__(self, provider: str, api_key: Optional[str] = None, additional_config: Optional[Dict[str, Any]] = None):
        """Initialize LLM config."""
        self.provider = provider
        self.api_key = api_key
        self.additional_config = additional_config or {}

class DatabaseConfig:
    """Database configuration."""
    
    def __init__(
        self,
        provider: DatabaseProvider,
        host: str = "localhost",
        port: int = 5432,
        database: str = "memory_system",
        username: str = "postgres",
        password: str = "postgres",
        ssl: bool = False
    ):
        """Initialize database config."""
        self.provider = provider
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.ssl = ssl
