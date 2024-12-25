"""
Memory store module.
"""

from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import Json
import pymongo
import numpy as np
from datetime import datetime, timedelta
from .models import Memory, MemoryLevel, MemoryType
from .config import DatabaseConfig, DatabaseProvider

class MemoryStore:
    """Store and retrieve memories."""
    
    def __init__(self, db_config: DatabaseConfig):
        """Initialize memory store."""
        self.db_config = db_config
        self.provider = db_config.provider
        
        # Initialize database connection
        if self.provider == DatabaseProvider.POSTGRESQL:
            self._init_postgresql()
        elif self.provider == DatabaseProvider.MONGODB:
            self._init_mongodb()
        else:
            raise ValueError(f"Unsupported database provider: {self.provider}")
    
    def _init_postgresql(self):
        """Initialize PostgreSQL connection."""
        try:
            self.db = psycopg2.connect(
                host=self.db_config.host,
                port=self.db_config.port,
                database=self.db_config.database,
                user=self.db_config.username,
                password=self.db_config.password,
                sslmode='require' if self.db_config.ssl else 'disable'
            )
            
            # Create memories table if it doesn't exist
            with self.db.cursor() as cursor:
                # Create vector similarity operator
                cursor.execute("""
                    CREATE OR REPLACE FUNCTION vector_similarity(a FLOAT[], b FLOAT[]) RETURNS FLOAT AS $$
                    DECLARE
                        dot_product FLOAT := 0;
                        norm_a FLOAT := 0;
                        norm_b FLOAT := 0;
                        i INTEGER;
                    BEGIN
                        IF array_length(a, 1) != array_length(b, 1) THEN
                            RETURN 0;
                        END IF;
                        
                        FOR i IN 1..array_length(a, 1) LOOP
                            dot_product := dot_product + (a[i] * b[i]);
                            norm_a := norm_a + (a[i] * a[i]);
                            norm_b := norm_b + (b[i] * b[i]);
                        END LOOP;
                        
                        IF norm_a = 0 OR norm_b = 0 THEN
                            RETURN 0;
                        END IF;
                        
                        RETURN dot_product / (sqrt(norm_a) * sqrt(norm_b));
                    END;
                    $$ LANGUAGE plpgsql IMMUTABLE;
                    
                    -- Create operator if it doesn't exist
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_operator WHERE oprname = '<->'
                            AND oprleft = 'float[]'::regtype
                            AND oprright = 'float[]'::regtype
                        ) THEN
                            CREATE OPERATOR <-> (
                                LEFTARG = FLOAT[],
                                RIGHTARG = FLOAT[],
                                FUNCTION = vector_similarity,
                                COMMUTATOR = <->
                            );
                        END IF;
                    END
                    $$;
                """)
                
                # Create memories table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id VARCHAR(36) PRIMARY KEY,
                        content TEXT NOT NULL,
                        embedding FLOAT[] NOT NULL,
                        level VARCHAR(50) NOT NULL,
                        memory_type VARCHAR(50) NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        metadata JSONB,
                        relevance_score FLOAT NOT NULL,
                        access_count INTEGER NOT NULL,
                        last_accessed TIMESTAMP,
                        tags TEXT[]
                    )
                """)
                self.db.commit()
                
        except Exception as e:
            raise Exception(f"Failed to initialize PostgreSQL: {str(e)}")
    
    def _init_mongodb(self):
        """Initialize MongoDB connection."""
        try:
            client = pymongo.MongoClient(
                host=self.db_config.host,
                port=self.db_config.port,
                username=self.db_config.username,
                password=self.db_config.password,
                ssl=self.db_config.ssl
            )
            self.db = client[self.db_config.database]
            
        except Exception as e:
            raise Exception(f"Failed to initialize MongoDB: {str(e)}")
    
    def store_memory(self, memory: Memory) -> None:
        """Store a memory."""
        if self.provider == DatabaseProvider.POSTGRESQL:
            with self.db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO memories (
                        id, content, embedding, level, memory_type,
                        timestamp, metadata, relevance_score,
                        access_count, last_accessed, tags
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    memory.id,
                    memory.content,
                    memory.embedding.tolist(),
                    memory.level.value if hasattr(memory.level, 'value') else memory.level,
                    memory.memory_type.value if hasattr(memory.memory_type, 'value') else memory.memory_type,
                    memory.timestamp,
                    Json(memory.metadata),
                    memory.relevance_score,
                    memory.access_count,
                    memory.last_accessed,
                    memory.tags
                ))
                self.db.commit()
                
        elif self.provider == DatabaseProvider.MONGODB:
            memory_dict = {
                "_id": memory.id,
                "content": memory.content,
                "embedding": memory.embedding.tolist(),
                "level": memory.level.value if hasattr(memory.level, 'value') else memory.level,
                "memory_type": memory.memory_type.value if hasattr(memory.memory_type, 'value') else memory.memory_type,
                "timestamp": memory.timestamp,
                "metadata": memory.metadata,
                "relevance_score": memory.relevance_score,
                "access_count": memory.access_count,
                "last_accessed": memory.last_accessed,
                "tags": memory.tags
            }
            self.db.memories.insert_one(memory_dict)
    
    def search_memories(
        self,
        query_embedding: Optional[np.ndarray] = None,
        level: Optional[MemoryLevel] = None,
        memory_type: Optional[MemoryType] = None,
        min_relevance: float = 0.0,
        max_results: int = 10,
        tags: Optional[List[str]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Memory]:
        """Search for memories based on query parameters."""
        if self.provider == DatabaseProvider.POSTGRESQL:
            # Build base query
            query = """
                SELECT *
                FROM memories
                WHERE 1=1
            """
            params = []
            
            # Add filters
            if level:
                query += " AND level = %s"
                params.append(level.value if hasattr(level, 'value') else level)
                
            if memory_type:
                query += " AND memory_type = %s"
                params.append(memory_type.value if hasattr(memory_type, 'value') else memory_type)
                
            if tags:
                query += " AND tags && %s"
                params.append(tags)
                
            # Add relevance score filter
            if min_relevance > 0:
                query += " AND relevance_score >= %s"
                params.append(min_relevance)
            
            # Add metadata filters
            if metadata_filters:
                for key, value in metadata_filters.items():
                    query += f" AND metadata->%s = %s"
                    params.extend([key, Json(value)])
            
            # Add similarity calculation and order by relevance
            if query_embedding is not None:
                query += """
                    ORDER BY (
                        embedding <-> %s
                    ) ASC
                """
                params.append(query_embedding.tolist())
            else:
                query += " ORDER BY timestamp DESC"
                
            # Add limit
            query += " LIMIT %s"
            params.append(max_results)
            
            # Execute query
            with self.db.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert rows to Memory objects
                memories = []
                for row in rows:
                    memory = Memory(
                        id=row[0],
                        content=row[1],
                        embedding=np.array(row[2]),
                        level=MemoryLevel(row[3]) if isinstance(row[3], str) else row[3],
                        memory_type=MemoryType(row[4]) if isinstance(row[4], str) else row[4],
                        timestamp=row[5],
                        metadata=row[6],
                        relevance_score=row[7],
                        access_count=row[8],
                        last_accessed=row[9],
                        tags=row[10]
                    )
                    memories.append(memory)
                
                return memories
                
        elif self.provider == DatabaseProvider.MONGODB:
            # Build query filter
            filter_query = {}
            
            if level:
                filter_query['level'] = level.value if hasattr(level, 'value') else level
                
            if memory_type:
                filter_query['memory_type'] = memory_type.value if hasattr(memory_type, 'value') else memory_type
                
            if tags:
                filter_query['tags'] = {'$in': tags}
                
            if min_relevance > 0:
                filter_query['relevance_score'] = {'$gte': min_relevance}
                
            if metadata_filters:
                for key, value in metadata_filters.items():
                    filter_query[f'metadata.{key}'] = value
            
            # Add vector similarity search
            pipeline = [
                {'$match': filter_query}
            ]
            
            if query_embedding is not None:
                pipeline.extend([
                    {
                        '$addFields': {
                            'similarity': {
                                '$reduce': {
                                    'input': {'$range': [0, {'$size': '$embedding'}]},
                                    'initialValue': 0,
                                    'in': {
                                        '$add': [
                                            '$$value',
                                            {
                                                '$multiply': [
                                                    {'$arrayElemAt': ['$embedding', '$$this']},
                                                    {'$arrayElemAt': [query_embedding.tolist(), '$$this']}
                                                ]
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    },
                    {'$sort': {'similarity': -1}}
                ])
            else:
                pipeline.append({'$sort': {'timestamp': -1}})
                
            pipeline.append({'$limit': max_results})
            
            # Execute query
            results = self.db.memories.aggregate(pipeline)
            
            # Convert results to Memory objects
            memories = []
            for doc in results:
                memory = Memory(
                    id=str(doc['_id']),
                    content=doc['content'],
                    embedding=np.array(doc['embedding']),
                    level=MemoryLevel(doc['level']) if isinstance(doc['level'], str) else doc['level'],
                    memory_type=MemoryType(doc['memory_type']) if isinstance(doc['memory_type'], str) else doc['memory_type'],
                    timestamp=doc['timestamp'],
                    metadata=doc['metadata'],
                    relevance_score=doc['relevance_score'],
                    access_count=doc['access_count'],
                    last_accessed=doc['last_accessed'],
                    tags=doc['tags']
                )
                memories.append(memory)
            
            return memories
            
        else:
            raise ValueError(f"Unsupported database provider: {self.provider}")
    
    def update_memory(self, memory: Memory) -> None:
        """Update an existing memory."""
        if self.provider == DatabaseProvider.POSTGRESQL:
            with self.db.cursor() as cursor:
                cursor.execute("""
                    UPDATE memories
                    SET content = %s,
                        embedding = %s,
                        level = %s,
                        memory_type = %s,
                        metadata = %s,
                        relevance_score = %s,
                        access_count = %s,
                        last_accessed = %s,
                        tags = %s
                    WHERE id = %s
                """, (
                    memory.content,
                    memory.embedding.tolist(),
                    memory.level.value if hasattr(memory.level, 'value') else memory.level,
                    memory.memory_type.value if hasattr(memory.memory_type, 'value') else memory.memory_type,
                    Json(memory.metadata),
                    memory.relevance_score,
                    memory.access_count,
                    memory.last_accessed,
                    memory.tags,
                    memory.id
                ))
                self.db.commit()
                
        elif self.provider == DatabaseProvider.MONGODB:
            memory_dict = {
                "content": memory.content,
                "embedding": memory.embedding.tolist(),
                "level": memory.level.value if hasattr(memory.level, 'value') else memory.level,
                "memory_type": memory.memory_type.value if hasattr(memory.memory_type, 'value') else memory.memory_type,
                "metadata": memory.metadata,
                "relevance_score": memory.relevance_score,
                "access_count": memory.access_count,
                "last_accessed": memory.last_accessed,
                "tags": memory.tags
            }
            self.db.memories.update_one(
                {"_id": memory.id},
                {"$set": memory_dict}
            )
    
    def delete_memory(self, memory_id: str) -> None:
        """Delete a memory by ID."""
        if self.provider == DatabaseProvider.POSTGRESQL:
            with self.db.cursor() as cursor:
                cursor.execute("DELETE FROM memories WHERE id = %s", (memory_id,))
                self.db.commit()
                
        elif self.provider == DatabaseProvider.MONGODB:
            self.db.memories.delete_one({"_id": memory_id})
