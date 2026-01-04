import os

PORT = int(os.getenv("PORT", "3000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "gateway-service")

RIDER_URL = os.getenv("RIDER_URL", "http://localhost:3001")
DRIVER_URL = os.getenv("DRIVER_URL", "http://localhost:3002")
TRIP_URL = os.getenv("TRIP_URL", "http://localhost:3003")
