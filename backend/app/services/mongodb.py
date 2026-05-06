from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from typing import Optional
import os


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        import traceback
        try:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
            print(f"[MongoDB] Attempting to connect to {mongodb_uri}...")

            cls.client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)

            # Test connection by ping first
            await cls.client.admin.command('ping')
            print("[MongoDB] Ping successful")

            # Only get database after successful ping
            cls.db = cls.client[os.getenv("MONGODB_DB", "chronicles")]
            print(f"[MongoDB] Database object created")

            # Create indexes
            await cls.create_indexes()

            print("[MongoDB] Connected successfully")
        except Exception as e:
            print(f"[MongoDB] Connection failed: {e}")
            print(f"[MongoDB] Traceback: {traceback.format_exc()}")
            # Continue without MongoDB for development
            cls.client = None
            cls.db = None
            print("[MongoDB] Running in standalone mode - case operations will work but documents require DB")
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
            print("[MongoDB] Disconnected")
    
    @classmethod
    async def create_indexes(cls):
        """Create database indexes"""
        if cls.db is None:
            return
        
        try:
            # Cases indexes
            await cls.db.cases.create_index("case_id", unique=True)
            await cls.db.cases.create_index("case_number", unique=True)
            
            # Documents indexes
            await cls.db.documents.create_index("document_id", unique=True)
            await cls.db.documents.create_index("case_id")
            await cls.db.documents.create_index([("case_id", 1), ("status", 1)])
            
            # Analysis results indexes
            await cls.db.analysis_results.create_index("document_id", unique=True)
            await cls.db.analysis_results.create_index("case_id")
            
            print("[MongoDB] Indexes created")
        except Exception as e:
            print(f"[MongoDB] Index creation failed: {e}")
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        return cls.db


mongodb = MongoDB()
