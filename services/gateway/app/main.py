from __future__ import annotations
from fastapi import FastAPI, HTTPException
import httpx

from .env import SERVICE_NAME, RIDER_URL, DRIVER_URL, TRIP_URL

app = FastAPI(title="API Gateway (BFF)")

@app.get("/health")
async def health():
    return {"ok": True, "service": SERVICE_NAME}

@app.get("/demo/services")
async def demo_services():
    return {
        "rider": RIDER_URL,
        "driver": DRIVER_URL,
        "trip": TRIP_URL
    }

@app.post("/demo/create-driver")
async def demo_create_driver(body: dict):
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(f"{DRIVER_URL}/drivers", json=body)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

@app.post("/demo/driver-available/{driver_id}")
async def demo_driver_available(driver_id: str):
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(f"{DRIVER_URL}/drivers/{driver_id}/available")
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

@app.post("/demo/request-trip")
async def demo_request_trip(body: dict):
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(f"{TRIP_URL}/trips", json=body)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()

@app.get("/demo/trips")
async def demo_trips():
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{TRIP_URL}/trips")
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()
