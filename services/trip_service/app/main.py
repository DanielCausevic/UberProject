from __future__ import annotations
from fastapi import FastAPI, HTTPException
from nanoid import generate

from shared.event_bus import RabbitBus
from shared.event_bus.types import BaseEvent, now_iso
from .env import RABBITMQ_URL, SERVICE_NAME
from .store import Trip, TripStore
from .schemas import CreateTripRequest

app = FastAPI(title="Trip Service")
store = TripStore()
bus = RabbitBus(RABBITMQ_URL)  # required

@app.on_event("startup")
async def startup() -> None:
    await bus.connect()

    async def on_driver_assigned(event: BaseEvent) -> None:
        if event.name != "driver.assigned":
            return
        trip_id = event.payload.get("trip_id")
        driver_id = event.payload.get("driver_id")
        if not trip_id or not driver_id:
            return
        try:
            store.assign_driver(trip_id, driver_id)
        except KeyError:
            return

    async def on_pricing_quoted(event: BaseEvent) -> None:
        if event.name != "pricing.quoted":
            return
        trip_id = event.payload.get("trip_id")
        est = event.payload.get("estimated_price_dkk")
        if not trip_id or est is None:
            return
        try:
            store.set_estimate(trip_id, float(est))
        except KeyError:
            return

    await bus.subscribe("driver.assigned", "trip.driver-assigned", on_driver_assigned)
    await bus.subscribe("pricing.quoted", "trip.pricing-quoted", on_pricing_quoted)

@app.on_event("shutdown")
async def shutdown() -> None:
    await bus.close()

@app.get("/health")
async def health():
    return {"ok": True, "service": SERVICE_NAME}

@app.get("/trips")
async def list_trips():
    return [t.__dict__ for t in store.list()]

@app.get("/trips/{trip_id}")
async def get_trip(trip_id: str):
    t = store.get(trip_id)
    if not t:
        raise HTTPException(status_code=404, detail="Trip not found")
    return t.__dict__

@app.post("/trips", status_code=201)
async def create_trip(req: CreateTripRequest):
    trip_id = generate(size=12)
    trip = store.create(Trip(
        id=trip_id,
        rider_id=req.rider_id,
        pickup=req.pickup.model_dump(),
        dropoff=req.dropoff.model_dump()
    ))

    event = BaseEvent(
        name="trip.requested",
        id=generate(size=12),
        ts=now_iso(),
        source=SERVICE_NAME,
        payload={
            "trip_id": trip_id,
            "rider_id": req.rider_id,
            "pickup": trip.pickup,
            "dropoff": trip.dropoff
        }
    )
    await bus.publish(event)
    return {"trip": trip.__dict__, "published": event.name}
