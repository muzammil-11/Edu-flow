from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
import os
from typing import Optional

class DatabaseConfig:
    """Manages MongoDB connections and LangGraph checkpointer configuration."""
    
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    _checkpointer: Optional[AsyncMongoDBSaver] = None
    
    @classmethod
    async def get_client(cls) -> AsyncIOMotorClient:
        """Get or create the MongoDB client."""
        if cls._client is None:
            mongodb_uri = os.getenv("MONGO_URL")
            if not mongodb_uri:
                raise ValueError("MONGO_URL not set in environment variables")
            cls._client = AsyncIOMotorClient(mongodb_uri)
            # Verify connection
            await cls._client.admin.command('ping')
        return cls._client
    
    @classmethod
    async def get_database(cls) -> AsyncIOMotorDatabase:
        """Get the MongoDB database instance."""
        if cls._db is None:
            client = await cls.get_client()
            db_name = os.getenv("DB_NAME", "test_database")
            cls._db = client[db_name]
        return cls._db
    
    @classmethod
    async def get_checkpointer(cls) -> AsyncMongoDBSaver:
        """Get the LangGraph MongoDB checkpointer."""
        if cls._checkpointer is None:
            client = await cls.get_client()
            cls._checkpointer = AsyncMongoDBSaver(client)
        return cls._checkpointer
    
    @classmethod
    async def close(cls):
        """Close the MongoDB connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
            cls._checkpointer = None