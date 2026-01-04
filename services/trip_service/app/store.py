from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .database import Trip as DBTrip, get_db, create_tables
import json

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
        create_tables()  # Create tables on initialization

    def create(self, trip: Trip) -> Trip:
        db_trip = DBTrip(
            id=trip.id,
            rider_id=trip.rider_id,
            pickup=json.dumps(trip.pickup),
            dropoff=json.dumps(trip.dropoff),
            status=trip.status,
            assigned_driver_id=trip.assigned_driver_id,
            estimated_price_dkk=trip.estimated_price_dkk,
            final_price_dkk=trip.final_price_dkk
        )
        with next(get_db()) as db:
            db.add(db_trip)
            db.commit()
            db.refresh(db_trip)
        return Trip(
            id=db_trip.id,
            rider_id=db_trip.rider_id,
            pickup=json.loads(db_trip.pickup),
            dropoff=json.loads(db_trip.dropoff),
            status=db_trip.status,
            assigned_driver_id=db_trip.assigned_driver_id,
            estimated_price_dkk=db_trip.estimated_price_dkk,
            final_price_dkk=db_trip.final_price_dkk
        )

    def get(self, trip_id: str) -> Optional[Trip]:
        with next(get_db()) as db:
            db_trip = db.query(DBTrip).filter(DBTrip.id == trip_id).first()
            if db_trip:
                return Trip(
                    id=db_trip.id,
                    rider_id=db_trip.rider_id,
                    pickup=json.loads(db_trip.pickup),
                    dropoff=json.loads(db_trip.dropoff),
                    status=db_trip.status,
                    assigned_driver_id=db_trip.assigned_driver_id,
                    estimated_price_dkk=db_trip.estimated_price_dkk,
                    final_price_dkk=db_trip.final_price_dkk
                )
        return None

    def list(self) -> list[Trip]:
        with next(get_db()) as db:
            db_trips = db.query(DBTrip).all()
            return [
                Trip(
                    id=t.id,
                    rider_id=t.rider_id,
                    pickup=json.loads(t.pickup),
                    dropoff=json.loads(t.dropoff),
                    status=t.status,
                    assigned_driver_id=t.assigned_driver_id,
                    estimated_price_dkk=t.estimated_price_dkk,
                    final_price_dkk=t.final_price_dkk
                )
                for t in db_trips
            ]

    def assign_driver(self, trip_id: str, driver_id: str) -> None:
        with next(get_db()) as db:
            db_trip = db.query(DBTrip).filter(DBTrip.id == trip_id).first()
            if not db_trip:
                raise KeyError("Trip not found")
            db_trip.status = "ASSIGNED"
            db_trip.assigned_driver_id = driver_id
            db.commit()

    def set_estimate(self, trip_id: str, estimated: float) -> None:
        with next(get_db()) as db:
            db_trip = db.query(DBTrip).filter(DBTrip.id == trip_id).first()
            if not db_trip:
                raise KeyError("Trip not found")
            db_trip.estimated_price_dkk = estimated
            db.commit()

    def complete(self, trip_id: str, final_price: float) -> None:
        with next(get_db()) as db:
            db_trip = db.query(DBTrip).filter(DBTrip.id == trip_id).first()
            if not db_trip:
                raise KeyError("Trip not found")
            db_trip.status = "COMPLETED"
            db_trip.final_price_dkk = final_price
            db.commit()
