import os
def must_get(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

PORT = int(os.getenv("PORT", "3005"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "payment-service")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")  # only needed for event-driven services
