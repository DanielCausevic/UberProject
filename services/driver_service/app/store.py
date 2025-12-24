from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class Driver:
    id: str
    name: str
    available: bool = False

class DriverStore:
    def __init__(self) -> None:
        self._drivers: dict[str, Driver] = {}

    def create(self, driver: Driver) -> Driver:
        self._drivers[driver.id] = driver
        return driver

    def get(self, driver_id: str) -> Optional[Driver]:
        return self._drivers.get(driver_id)

    def list(self) -> list[Driver]:
        return list(self._drivers.values())

    def set_available(self, driver_id: str, available: bool = True) -> Driver:
        d = self._drivers.get(driver_id)
        if not d:
            raise KeyError("Driver not found")
        d.available = available
        return d

    def pick_available(self) -> Optional[Driver]:
        for d in self._drivers.values():
            if d.available:
                return d
        return None
