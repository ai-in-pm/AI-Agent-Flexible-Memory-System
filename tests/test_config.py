"""Test configuration functionality."""

import pytest
from memory_system.config import LLMConfig, DatabaseConfig, DatabaseProvider

def test_llm_config():
    """Test LLM configuration."""
    config = LLMConfig(
        provider="openai",
        api_key="test-key",
        additional_config={
            "temperature": 0.7,
            "model": "gpt-4-turbo-preview"
        }
    )
    
    assert config.provider == "openai"
    assert config.api_key == "test-key"
    assert config.additional_config["temperature"] == 0.7
    assert config.additional_config["model"] == "gpt-4-turbo-preview"

def test_database_config():
    """Test database configuration."""
    config = DatabaseConfig(
        provider=DatabaseProvider.POSTGRESQL,
        host="localhost",
        port=5433,
        database="memory_system_test",
        username="memory_system",
        password="memory_system_pass"
    )
    
    assert config.provider == DatabaseProvider.POSTGRESQL
    assert config.host == "localhost"
    assert config.port == 5433
    assert config.database == "memory_system_test"
    assert config.username == "memory_system"
    assert config.password == "memory_system_pass"
