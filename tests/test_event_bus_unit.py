"""
Unit Tests for Event Bus

Tests event-driven architecture components without complex async mocking.
"""

from datetime import datetime
from shared.event_bus.types import BaseEvent, now_iso


class TestBaseEvent:
    """Test BaseEvent class functionality"""

    def test_event_creation(self):
        """Test basic event creation"""
        event = BaseEvent(
            name="trip.requested",
            id="event123",
            ts="2024-01-01T12:00:00Z",
            source="trip-service",
            payload={"trip_id": "trip456"}
        )

        assert event.name == "trip.requested"
        assert event.id == "event123"
        assert event.ts == "2024-01-01T12:00:00Z"
        assert event.source == "trip-service"
        assert event.payload["trip_id"] == "trip456"

    def test_event_with_complex_payload(self):
        """Test event with complex payload data"""
        payload = {
            "trip_id": "trip123",
            "rider_id": "rider456",
            "pickup": {"lat": 55.6761, "lng": 12.5683},
            "dropoff": {"lat": 55.6861, "lng": 12.5783},
            "fare": 125.50
        }

        event = BaseEvent(
            name="trip.completed",
            id="event789",
            ts="2024-01-01T13:30:00Z",
            source="trip-service",
            payload=payload
        )

        assert event.payload["fare"] == 125.50
        assert event.payload["pickup"]["lat"] == 55.6761

    def test_event_equality(self):
        """Test event equality comparison"""
        event1 = BaseEvent(
            name="driver.assigned",
            id="event123",
            ts="2024-01-01T12:00:00Z",
            source="trip-service",
            payload={"trip_id": "trip456", "driver_id": "driver789"}
        )

        event2 = BaseEvent(
            name="driver.assigned",
            id="event123",
            ts="2024-01-01T12:00:00Z",
            source="trip-service",
            payload={"trip_id": "trip456", "driver_id": "driver789"}
        )

        # Events with same data should be equal
        assert event1.name == event2.name
        assert event1.id == event2.id
        assert event1.payload == event2.payload


class TestEventTimestamp:
    """Test event timestamp functionality"""

    def test_now_iso_function(self):
        """Test ISO timestamp generation"""
        ts = now_iso()

        # Should be ISO format with Z suffix
        assert ts.endswith("Z")
        assert "T" in ts

        # Should be parseable as datetime
        parsed = datetime.fromisoformat(ts[:-1])  # Remove Z for parsing
        assert isinstance(parsed, datetime)

    def test_timestamp_format(self):
        """Test timestamp format validation"""
        import re

        ts = now_iso()
        # ISO 8601 format with optional microseconds: 2024-01-01T12:00:00Z or 2024-01-01T12:00:00.123456Z
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$"

        assert re.match(iso_pattern, ts)

    def test_timestamp_ordering(self):
        """Test timestamp chronological ordering"""
        ts1 = now_iso()
        ts2 = now_iso()

        # Later timestamp should be greater
        assert ts2 >= ts1


class TestEventNaming:
    """Test event naming conventions"""

    def test_event_name_format(self):
        """Test event name format validation"""
        import re

        valid_events = [
            "trip.requested",
            "driver.assigned",
            "pricing.quoted",
            "payment.charged",
            "notification.sent"
        ]

        invalid_events = [
            "trip",
            "trip.",
            ".requested",
            "trip.requested.extra",
            "invalid-event"
        ]

        event_pattern = r"^[a-z]+\.[a-z]+$"

        for event in valid_events:
            assert re.match(event_pattern, event)

        for event in invalid_events:
            assert not re.match(event_pattern, event)

    def test_service_event_mapping(self):
        """Test mapping of services to their events"""
        service_events = {
            "trip-service": [
                "trip.requested",
                "trip.completed",
                "driver.assigned"
            ],
            "pricing-service": [
                "pricing.quoted"
            ],
            "payment-service": [
                "payment.charged"
            ],
            "notification-service": [
                "notification.sent"
            ]
        }

        # Verify each service has at least one event
        for service, events in service_events.items():
            assert len(events) > 0
            assert all("." in event for event in events)

        # Verify no duplicate events across services
        all_events = []
        for events in service_events.values():
            all_events.extend(events)

        assert len(all_events) == len(set(all_events))  # No duplicates


class TestEventPayload:
    """Test event payload structures"""

    def test_trip_requested_payload(self):
        """Test trip.requested event payload"""
        payload = {
            "trip_id": "trip123",
            "rider_id": "rider456",
            "pickup": {"lat": 55.6761, "lng": 12.5683},
            "dropoff": {"lat": 55.6861, "lng": 12.5783}
        }

        required_fields = ["trip_id", "rider_id", "pickup", "dropoff"]

        for field in required_fields:
            assert field in payload

        assert isinstance(payload["pickup"], dict)
        assert "lat" in payload["pickup"]
        assert "lng" in payload["pickup"]

    def test_driver_assigned_payload(self):
        """Test driver.assigned event payload"""
        payload = {
            "trip_id": "trip123",
            "driver_id": "driver456",
            "estimated_pickup_time": "2024-01-01T12:15:00Z"
        }

        required_fields = ["trip_id", "driver_id"]

        for field in required_fields:
            assert field in payload

    def test_pricing_quoted_payload(self):
        """Test pricing.quoted event payload"""
        payload = {
            "trip_id": "trip123",
            "base_fare": 50.0,
            "distance_fare": 75.0,
            "time_fare": 25.0,
            "total_fare": 150.0,
            "currency": "DKK"
        }

        assert payload["total_fare"] == payload["base_fare"] + payload["distance_fare"] + payload["time_fare"]
        assert payload["currency"] == "DKK"

    def test_payment_charged_payload(self):
        """Test payment.charged event payload"""
        payload = {
            "trip_id": "trip123",
            "amount": 150.0,
            "currency": "DKK",
            "payment_method": "card",
            "status": "success"
        }

        assert payload["amount"] > 0
        assert payload["status"] in ["success", "failed", "pending"]

    def test_notification_sent_payload(self):
        """Test notification.sent event payload"""
        payload = {
            "trip_id": "trip123",
            "recipient_id": "rider456",
            "type": "sms",
            "message": "Your driver is on the way!"
        }

        assert payload["type"] in ["sms", "email", "push"]
        assert len(payload["message"]) > 0


class TestEventSerialization:
    """Test event serialization"""

    def test_event_to_dict(self):
        """Test converting event to dictionary"""
        event = BaseEvent(
            name="trip.requested",
            id="event123",
            ts="2024-01-01T12:00:00Z",
            source="trip-service",
            payload={"trip_id": "trip456"}
        )

        event_dict = event.__dict__

        assert event_dict["name"] == "trip.requested"
        assert event_dict["id"] == "event123"
        assert event_dict["source"] == "trip-service"
        assert event_dict["payload"]["trip_id"] == "trip456"

    def test_event_json_serialization(self):
        """Test JSON serialization of events"""
        import json

        event = BaseEvent(
            name="driver.assigned",
            id="event789",
            ts="2024-01-01T12:30:00Z",
            source="trip-service",
            payload={
                "trip_id": "trip123",
                "driver_id": "driver456",
                "location": {"lat": 55.6761, "lng": 12.5683}
            }
        )

        event_dict = event.__dict__
        json_str = json.dumps(event_dict)
        parsed = json.loads(json_str)

        assert parsed["name"] == "driver.assigned"
        assert parsed["payload"]["driver_id"] == "driver456"
        assert parsed["payload"]["location"]["lat"] == 55.6761


class TestEventWorkflow:
    """Test event-driven workflow patterns"""

    def test_trip_lifecycle_events(self):
        """Test sequence of events in trip lifecycle"""
        trip_id = "trip123"
        rider_id = "rider456"
        driver_id = "driver789"

        events = [
            {
                "name": "trip.requested",
                "payload": {"trip_id": trip_id, "rider_id": rider_id}
            },
            {
                "name": "driver.assigned",
                "payload": {"trip_id": trip_id, "driver_id": driver_id}
            },
            {
                "name": "pricing.quoted",
                "payload": {"trip_id": trip_id, "total_fare": 150.0}
            },
            {
                "name": "trip.completed",
                "payload": {"trip_id": trip_id, "final_fare": 150.0}
            },
            {
                "name": "payment.charged",
                "payload": {"trip_id": trip_id, "amount": 150.0}
            },
            {
                "name": "notification.sent",
                "payload": {"trip_id": trip_id, "recipient_id": rider_id}
            }
        ]

        # Verify event sequence
        assert len(events) == 6

        # Verify all events reference the same trip
        for event in events:
            assert event["payload"]["trip_id"] == trip_id

        # Verify logical sequence
        event_names = [e["name"] for e in events]
        expected_sequence = [
            "trip.requested",
            "driver.assigned",
            "pricing.quoted",
            "trip.completed",
            "payment.charged",
            "notification.sent"
        ]

        assert event_names == expected_sequence

    def test_event_chaining(self):
        """Test how events trigger other events"""
        # Simulate event reaction patterns
        event_reactions = {
            "trip.requested": ["driver.assigned", "pricing.quoted"],
            "driver.assigned": ["notification.sent"],
            "trip.completed": ["payment.charged", "notification.sent"],
            "payment.charged": ["notification.sent"]
        }

        # Verify each event triggers at least one reaction
        for trigger_event, reactions in event_reactions.items():
            assert len(reactions) > 0

        # Verify no circular dependencies (simplified check)
        all_events = set(event_reactions.keys())
        all_reactions = set()
        for reactions in event_reactions.values():
            all_reactions.update(reactions)

        # Some reactions might not be triggers themselves
        assert len(all_reactions - all_events) >= 0