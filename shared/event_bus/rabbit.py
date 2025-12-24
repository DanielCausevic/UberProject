from __future__ import annotations
import json
from typing import Awaitable, Callable, Optional

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from .types import BaseEvent

Handler = Callable[[BaseEvent], Awaitable[None]]

class RabbitBus:
    def __init__(self, url: str, exchange_name: str = "events") -> None:
        self.url = url
        self.exchange_name = exchange_name
        self._conn: Optional[aio_pika.RobustConnection] = None
        self._channel: Optional[aio_pika.RobustChannel] = None
        self._exchange: Optional[aio_pika.Exchange] = None

    async def connect(self) -> None:
        self._conn = await aio_pika.connect_robust(self.url)
        self._channel = await self._conn.channel()
        self._exchange = await self._channel.declare_exchange(
            self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )

    async def close(self) -> None:
        if self._channel:
            await self._channel.close()
        if self._conn:
            await self._conn.close()

    async def publish(self, event: BaseEvent) -> None:
        if not self._exchange:
            raise RuntimeError("RabbitBus not connected")
        body = json.dumps(event.__dict__).encode("utf-8")
        msg = aio_pika.Message(body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT)
        await self._exchange.publish(msg, routing_key=event.name)

    async def subscribe(self, event_name: str, queue_name: str, handler: Handler) -> None:
        if not self._channel or not self._exchange:
            raise RuntimeError("RabbitBus not connected")

        queue = await self._channel.declare_queue(queue_name, durable=True)
        await queue.bind(self._exchange, routing_key=event_name)

        async def _on_message(message: AbstractIncomingMessage) -> None:
            async with message.process(requeue=False):
                data = json.loads(message.body.decode("utf-8"))
                event = BaseEvent(**data)
                await handler(event)

        await queue.consume(_on_message)
