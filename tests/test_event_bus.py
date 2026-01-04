import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
import aio_pika
from shared.event_bus.rabbit import RabbitBus
from shared.event_bus.types import BaseEvent, now_iso


class TestBaseEvent:
    """Test BaseEvent dataclass"""

    def test_base_event_creation(self):
        """Test basic event creation"""
        event = BaseEvent(
            name="trip.requested",
            id="event123",
            ts="2025-12-29T10:00:00Z",
            source="trip-service",
            payload={"trip_id": "trip123", "rider_id": "rider456"}
        )

        assert event.name == "trip.requested"
        assert event.id == "event123"
        assert event.ts == "2025-12-29T10:00:00Z"
        assert event.source == "trip-service"
        assert event.payload == {"trip_id": "trip123", "rider_id": "rider456"}

    def test_base_event_serialization(self):
        """Test event JSON serialization"""
        event = BaseEvent(
            name="driver.assigned",
            id="event456",
            ts="2025-12-29T10:30:00Z",
            source="driver-service",
            payload={"trip_id": "trip123", "driver_id": "driver789"}
        )

        event_dict = event.__dict__
        json_str = json.dumps(event_dict)
        parsed = json.loads(json_str)

        assert parsed["name"] == "driver.assigned"
        assert parsed["payload"]["driver_id"] == "driver789"


class TestNowIso:
    """Test now_iso utility function"""

    @patch('shared.event_bus.types.datetime')
    def test_now_iso_format(self, mock_datetime):
        """Test ISO timestamp format"""
        mock_datetime.utcnow.return_value.isoformat.return_value = "2025-12-29T10:00:00"

        result = now_iso()

        assert result == "2025-12-29T10:00:00Z"
        mock_datetime.utcnow.assert_called_once()


class TestRabbitBus:
    """Test RabbitBus class"""

    @pytest.fixture
    def rabbit_bus(self):
        """Create RabbitBus instance for testing"""
        return RabbitBus("amqp://test:test@localhost:5672/")

    @patch('shared.event_bus.rabbit.aio_pika')
    @pytest.mark.asyncio
    async def test_connect_success(self, mock_aio_pika, rabbit_bus):
        """Test successful connection to RabbitMQ"""
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()

        mock_aio_pika.connect_robust = AsyncMock(return_value=mock_connection)
        mock_connection.channel = AsyncMock(return_value=mock_channel)
        mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)

        await rabbit_bus.connect()

        assert rabbit_bus._conn == mock_connection
        assert rabbit_bus._channel == mock_channel
        assert rabbit_bus._exchange == mock_exchange

        mock_aio_pika.connect_robust.assert_called_once_with("amqp://test:test@localhost:5672/")
        mock_channel.declare_exchange.assert_called_once()

    @patch('shared.event_bus.rabbit.aio_pika')
    @pytest.mark.asyncio
    async def test_connect_retry_on_failure(self, mock_aio_pika, rabbit_bus):
        """Test connection retry on failure"""
        mock_aio_pika.connect_robust.side_effect = Exception("Connection failed")

        with pytest.raises(Exception, match="Connection failed"):
            await rabbit_bus.connect()

        # Should have tried 10 times (max retries)
        assert mock_aio_pika.connect_robust.call_count == 10

    @patch('shared.event_bus.rabbit.aio_pika')
    @pytest.mark.asyncio
    async def test_connect_max_retries_exceeded(self, mock_aio_pika, rabbit_bus):
        """Test connection failure after max retries"""
        mock_aio_pika.connect_robust.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await rabbit_bus.connect()

        assert mock_aio_pika.connect_robust.call_count == 10  # Max attempts

    @pytest.mark.asyncio
    async def test_close_connection(self, rabbit_bus):
        """Test closing RabbitMQ connection"""
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()

        rabbit_bus._conn = mock_connection
        rabbit_bus._channel = mock_channel

        await rabbit_bus.close()

        mock_channel.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_without_connection(self, rabbit_bus):
        """Test closing when no connection exists"""
        # Should not raise any errors
        await rabbit_bus.close()

        # Connection should remain None
        assert rabbit_bus._conn is None
        assert rabbit_bus._channel is None
        assert rabbit_bus._exchange is None

    @pytest.mark.asyncio
    async def test_publish_without_connection(self, rabbit_bus):
        """Test publishing without established connection"""
        event = BaseEvent(
            name="test.event",
            id="event123",
            ts="2025-12-29T10:00:00Z",
            source="test-service",
            payload={"key": "value"}
        )

        with pytest.raises(RuntimeError, match="RabbitBus not connected"):
            await rabbit_bus.publish(event)

    @pytest.mark.asyncio
    async def test_publish_success(self, rabbit_bus):
        """Test successful event publishing"""
        # Setup mock connection
        mock_exchange = AsyncMock()
        rabbit_bus._exchange = mock_exchange

        with patch('shared.event_bus.rabbit.aio_pika.Message') as mock_message_class:
            mock_message = MagicMock()
            mock_message_class.return_value = mock_message

            event = BaseEvent(
                name="trip.requested",
                id="event123",
                ts="2025-12-29T10:00:00Z",
                source="trip-service",
                payload={"trip_id": "trip123"}
            )

            await rabbit_bus.publish(event)

            # Verify message creation and publishing
            mock_message_class.assert_called_once()
            call_args = mock_message_class.call_args
            assert call_args[1]['delivery_mode'] == aio_pika.DeliveryMode.PERSISTENT

            mock_exchange.publish.assert_called_once_with(
                mock_message,
                routing_key="trip.requested"
            )

    @pytest.mark.asyncio
    async def test_subscribe_without_connection(self, rabbit_bus):
        """Test subscribing without established connection"""
        async def dummy_handler(event):
            pass

        with pytest.raises(RuntimeError, match="RabbitBus not connected"):
            await rabbit_bus.subscribe("test.event", "test-queue", dummy_handler)

    @pytest.mark.asyncio
    async def test_subscribe_success(self, rabbit_bus):
        """Test successful event subscription"""
        # Setup mocks
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        mock_queue = AsyncMock()

        rabbit_bus._channel = mock_channel
        rabbit_bus._exchange = mock_exchange
        mock_channel.declare_queue.return_value = mock_queue

        async def test_handler(event):
            pass

        await rabbit_bus.subscribe("trip.requested", "trip-queue", test_handler)

        # Verify queue declaration and binding
        mock_channel.declare_queue.assert_called_once_with("trip-queue", durable=True)
        mock_queue.bind.assert_called_once_with(mock_exchange, routing_key="trip.requested")
        mock_queue.consume.assert_called_once()


class TestEventTypes:
    """Test all supported event types"""

    def test_all_event_names_supported(self):
        """Test that all event names are valid"""
        valid_events = [
            "trip.requested",
            "driver.assigned",
            "pricing.quoted",
            "trip.completed",
            "payment.charged",
            "notification.sent"
        ]

        for event_name in valid_events:
            event = BaseEvent(
                name=event_name,
                id=f"test-{event_name.replace('.', '-')}",
                ts="2025-12-29T10:00:00Z",
                source="test-service",
                payload={"event_type": event_name}
            )
            assert event.name == event_name
            assert event.id == f"test-{event_name.replace('.', '-')}"
            assert event.source == "test-service"
            assert event.payload["event_type"] == event_name

    def test_event_payload_types(self):
        """Test that events can contain various payload types and serialize properly"""
        # Test with different payload types
        test_cases = [
            {"string": "value", "number": 42},
            {"list": [1, 2, 3], "nested": {"key": "value"}},
            {"boolean": True, "null": None},
        ]

        for i, payload in enumerate(test_cases):
            event = BaseEvent(
                name="test.event",
                id=f"test{i}",
                ts="2025-12-29T10:00:00Z",
                source="test-service",
                payload=payload
            )
            assert event.payload == payload

            # Test JSON serialization works
            event_dict = event.__dict__
            json_str = json.dumps(event_dict)
            parsed = json.loads(json_str)
            assert parsed["payload"] == payload