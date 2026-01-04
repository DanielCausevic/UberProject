from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from datetime import datetime
from typing import Optional, Dict, Any

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://app:app@localhost:27017/uber")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def connect_to_mongo():
    """Connect to MongoDB"""
    try:
        db.client = AsyncIOMotorClient(MONGODB_URL)
        db.database = db.client.get_database("uber")
        # Test the connection
        await db.client.admin.command('ping')
        print("Connected to MongoDB")
    except ConnectionFailure:
        print("Failed to connect to MongoDB")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database

# Rider document model
def create_rider_document(
    rider_id: str,
    name: str,
    email: str,
    phone: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a rider document for MongoDB"""
    document = {
        "_id": rider_id,
        "name": name,
        "email": email,
        "phone": phone,
        "preferences": preferences or {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    return document