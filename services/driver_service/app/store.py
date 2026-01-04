from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .database import Driver as DBDriver, get_db, create_tables

@dataclass
class Driver:
    id: str
    name: str
    available: bool = False

class DriverStore:
    def __init__(self) -> None:
        create_tables()  # Create tables on initialization

    def create(self, driver: Driver) -> DBDriver:
        db_driver = DBDriver(
            id=driver.id,
            name=driver.name,
            available=driver.available
        )
        with next(get_db()) as db:
            db.add(db_driver)
            db.commit()
            db.refresh(db_driver)
        return db_driver

    def get(self, driver_id: str) -> Optional[DBDriver]:
        with next(get_db()) as db:
            return db.query(DBDriver).filter(DBDriver.id == driver_id).first()

    def list(self) -> list[DBDriver]:
        with next(get_db()) as db:
            return db.query(DBDriver).all()

    def pick_available(self) -> Optional[DBDriver]:
        with next(get_db()) as db:
            return db.query(DBDriver).filter(DBDriver.available == True).first()

    def set_available(self, driver_id: str, available: bool) -> None:
        with next(get_db()) as db:
            driver = db.query(DBDriver).filter(DBDriver.id == driver_id).first()
            if not driver:
                raise KeyError("Driver not found")
            driver.available = available
            db.commit()
