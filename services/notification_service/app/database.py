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

# Notification document model
def create_notification_document(
    notification_id: str,
    user_id: str,
    user_type: str,
    notification_type: str,
    title: str,
    message: str
) -> Dict[str, Any]:
    """Create a notification document for MongoDB"""
    return {
        "_id": notification_id,
        "user_id": user_id,
        "user_type": user_type,
        "type": notification_type,
        "title": title,
        "message": message,
        "sent": False,
        "sent_at": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }