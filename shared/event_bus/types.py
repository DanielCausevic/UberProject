from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Any, Dict
from datetime import datetime

EventName = Literal[
    "trip.requested",
    "driver.assigned",
    "pricing.quoted",
    "trip.completed",
    "payment.charged",
    "notification.sent",
]

@dataclass
class BaseEvent:
    name: EventName
    id: str
    ts: str
    source: str
    payload: Dict[str, Any]

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"
