# AI Agent Flexible Memory System

A flexible and modular memory system designed for AI agents, supporting both basic and multi-modal memory operations with PostgreSQL and MongoDB storage backends.

## Features

- **Flexible Storage**: Support for both PostgreSQL (with vector similarity search) and MongoDB
- **Multi-Modal Memory**: Store and retrieve various types of memory content
- **Memory Levels**: Organize memories by different levels (Individual, Team, Organization)
- **Memory Types**: Support for different memory types (Experience, Knowledge)
- **Vector Similarity Search**: Efficient similarity-based memory retrieval
- **Metadata & Tagging**: Rich metadata and tagging support for better memory organization

## Requirements

- Python 3.8+
- PostgreSQL 12+ or MongoDB 4.4+
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ai-in-pm/AI-Agent-Flexible-Memory-System.git
cd ai-agent-flexible-memory-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables in `.env`:
```env
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=memory_system_demo
POSTGRES_USER=memory_system
POSTGRES_PASSWORD=memory_system_pass

# MongoDB Configuration
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=memory_system_demo
MONGODB_USER=memory_system
MONGODB_PASSWORD=memory_system_pass

# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key
```

## Usage

### Basic Memory Operations

```python
from memory_system import MemoryManager, MemoryLevel, MemoryType
from memory_system.config import LLMConfig, DatabaseConfig, DatabaseProvider

# Initialize configurations
llm_config = LLMConfig(
    provider="openai",
    api_key="your-api-key",
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

# Create memory manager
memory_manager = MemoryManager(llm_config=llm_config, db_config=db_config)

# Add a memory
memory = memory_manager.add_experience(
    content="Important team meeting about project roadmap",
    level=MemoryLevel.TEAM,
    memory_type=MemoryType.EXPERIENCE,
    tags=["meeting", "roadmap", "planning"],
    metadata={"participants": ["Alice", "Bob", "Charlie"]}
)

# Query memories
query = MemoryQuery(
    content="project planning meeting",
    level=MemoryLevel.TEAM,
    tags=["meeting"],
    max_results=5
)
results = memory_manager.search_memories(query)
```

### Multi-Modal Memory Operations

See `demonstrations/advanced_examples/multi_modal_memory.py` for examples of working with multi-modal memories.

## Running Demonstrations

The project includes demonstrations for both basic and advanced memory operations:

```bash
python demonstrations/run_demonstrations.py
```

## Project Structure

```
ai-agent-flexible-memory-system/
├── memory_system/
│   ├── __init__.py
│   ├── config.py           # Configuration classes
│   ├── embeddings.py       # Embedding generation
│   ├── memory_manager.py   # Main memory management
│   ├── memory_store.py     # Storage backend
│   └── models.py           # Data models
├── demonstrations/
│   ├── basic_examples/
│   │   └── memory_operations.py
│   └── advanced_examples/
│       └── multi_modal_memory.py
├── tests/
│   └── ...
├── .env
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
