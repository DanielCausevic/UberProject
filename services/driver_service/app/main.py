from __future__ import annotations
from fastapi import FastAPI, HTTPException
from nanoid import generate

from shared.event_bus import RabbitBus
from shared.event_bus.types import BaseEvent, now_iso
from .env import RABBITMQ_URL, SERVICE_NAME
from .store import Driver, DriverStore
from .schemas import CreateDriverRequest

app = FastAPI(title="Driver Service")
store = DriverStore()
bus = RabbitBus(RABBITMQ_URL)

@app.on_event("startup")
async def startup() -> None:
    await bus.connect()

    async def on_trip_requested(event: BaseEvent) -> None:
        if event.name != "trip.requested":
            return
        trip_id = event.payload.get("trip_id")
        if not trip_id:
            return

        driver = store.pick_available()
        if not driver:
            return

        store.set_available(driver.id, False)

        assigned = BaseEvent(
            name="driver.assigned",
            id=generate(size=12),
            ts=now_iso(),
            source=SERVICE_NAME,
            payload={"trip_id": trip_id, "driver_id": driver.id},
        )
        await bus.publish(assigned)

    await bus.subscribe("trip.requested", "driver.trip-requested", on_trip_requested)

@app.on_event("shutdown")
async def shutdown() -> None:
    await bus.close()

@app.get("/health")
async def health():
    return {"ok": True, "service": SERVICE_NAME}

@app.get("/drivers")
async def list_drivers():
    return [d.__dict__ for d in store.list()]

@app.post("/drivers", status_code=201)
async def create_driver(req: CreateDriverRequest):
    d = store.create(Driver(id=generate(size=12), name=req.name))
    return d.__dict__

@app.post("/drivers/{driver_id}/available")
async def set_available(driver_id: str):
    try:
        d = store.set_available(driver_id, True)
    except KeyError:
        raise HTTPException(status_code=404, detail="Driver not found")
    return d.__dict__
