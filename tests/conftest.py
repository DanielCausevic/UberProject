import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing HTTP calls"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = Mock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_trip_data():
    """Sample trip data for testing"""
    return {
        "rider_id": "test-rider-123",
        "pickup": {"lat": 55.6761, "lng": 12.5683},
        "dropoff": {"lat": 55.6761, "lng": 12.5683}
    }


@pytest.fixture
def sample_driver_data():
    """Sample driver data for testing"""
    return {
        "name": "Test Driver",
        "available": False
    }


@pytest.fixture
def sample_pricing_rule():
    """Sample pricing rule data for testing"""
    return {
        "id": "standard_fare",
        "name": "Standard Fare",
        "base_fare": 50.0,
        "per_km_rate": 10.0,
        "per_minute_rate": 2.0,
        "minimum_fare": 75.0,
        "active": True
    }


@pytest.fixture
def sample_rider_document():
    """Sample rider document for MongoDB testing"""
    return {
        "_id": "rider123",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+4512345678",
        "preferences": {
            "language": "en",
            "notifications": True
        },
        "created_at": "2025-12-29T10:00:00Z",
        "updated_at": "2025-12-29T10:00:00Z"
    }


@pytest.fixture
def sample_notification_document():
    """Sample notification document for MongoDB testing"""
    return {
        "_id": "notif123",
        "user_id": "user456",
        "user_type": "rider",
        "type": "trip_assigned",
        "title": "Trip Assigned",
        "message": "Your driver is on the way!",
        "sent": False,
        "sent_at": None,
        "created_at": "2025-12-29T10:00:00Z",
        "updated_at": "2025-12-29T10:00:00Z"
    }


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "mongodb: mark test as requiring MongoDB"
    )
    config.addinivalue_line(
        "markers", "redis: mark test as requiring Redis"
    )
    config.addinivalue_line(
        "markers", "postgresql: mark test as requiring PostgreSQL"
    )


# Test utilities
def assert_trip_structure(trip_dict):
    """Assert that a trip dictionary has the correct structure"""
    required_fields = ["id", "rider_id", "pickup", "dropoff", "status"]
    for field in required_fields:
        assert field in trip_dict

    # Check coordinate structure
    assert "lat" in trip_dict["pickup"]
    assert "lng" in trip_dict["pickup"]
    assert "lat" in trip_dict["dropoff"]
    assert "lng" in trip_dict["dropoff"]


def assert_driver_structure(driver_dict):
    """Assert that a driver dictionary has the correct structure"""
    required_fields = ["id", "name", "available"]
    for field in required_fields:
        assert field in driver_dict

    assert isinstance(driver_dict["available"], bool)


def assert_event_structure(event):
    """Assert that an event has the correct structure"""
    required_fields = ["name", "id", "ts", "source", "payload"]
    for field in required_fields:
        assert hasattr(event, field)

    assert event.name in [
        "trip.requested", "driver.assigned", "pricing.quoted",
        "trip.completed", "payment.charged", "notification.sent"
    ]


def wait_for_event_processing(seconds=2):
    """Wait for event processing to complete"""
    import time
    time.sleep(seconds)


# Environment setup for tests
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    import os

    # Set test database URLs if not already set
    if "DATABASE_URL" not in os.environ:
        os.environ["DATABASE_URL"] = "postgresql://app:app@localhost:5432/uber_test"

    if "MONGODB_URL" not in os.environ:
        os.environ["MONGODB_URL"] = "mongodb://app:app@localhost:27017/uber_test"

    if "REDIS_URL" not in os.environ:
        os.environ["REDIS_URL"] = "redis://localhost:6379"

    if "RABBITMQ_URL" not in os.environ:
        os.environ["RABBITMQ_URL"] = "amqp://app:app@localhost:5672/"