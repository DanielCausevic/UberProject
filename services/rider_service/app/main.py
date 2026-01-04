from fastapi import FastAPI
from .env import SERVICE_NAME
from .database import connect_to_mongo, close_mongo_connection

app = FastAPI(title="Rider Service")

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()

@app.get("/health")
async def health():
    return {"ok": True, "service": SERVICE_NAME}

# TODO: Implement endpoints + event subscriptions/publishing.
