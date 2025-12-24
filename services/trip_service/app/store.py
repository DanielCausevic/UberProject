from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class Trip:
    id: str
    rider_id: str
    pickup: dict
    dropoff: dict
    status: str = "REQUESTED"
    assigned_driver_id: Optional[str] = None
    estimated_price_dkk: Optional[float] = None
    final_price_dkk: Optional[float] = None

class TripStore:
    def __init__(self) -> None:
        self._trips: dict[str, Trip] = {}

    def create(self, trip: Trip) -> Trip:
        self._trips[trip.id] = trip
        return trip

    def get(self, trip_id: str) -> Optional[Trip]:
        return self._trips.get(trip_id)

    def list(self) -> list[Trip]:
        return list(self._trips.values())

    def assign_driver(self, trip_id: str, driver_id: str) -> None:
        t = self._trips.get(trip_id)
        if not t:
            raise KeyError("Trip not found")
        t.status = "ASSIGNED"
        t.assigned_driver_id = driver_id

    def set_estimate(self, trip_id: str, estimated: float) -> None:
        t = self._trips.get(trip_id)
        if not t:
            raise KeyError("Trip not found")
        t.estimated_price_dkk = estimated

    def complete(self, trip_id: str, final_price: float) -> None:
        t = self._trips.get(trip_id)
        if not t:
            raise KeyError("Trip not found")
        t.status = "COMPLETED"
        t.final_price_dkk = final_price
