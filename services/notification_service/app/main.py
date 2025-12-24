from fastapi import FastAPI
from .env import SERVICE_NAME

app = FastAPI(title="Notification Service")

@app.get("/health")
async def health():
    return {"ok": True, "service": SERVICE_NAME}

# TODO: Implement endpoints + event subscriptions/publishing.
