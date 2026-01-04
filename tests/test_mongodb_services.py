import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.rider_service.app.database import connect_to_mongo, close_mongo_connection, get_database, create_rider_document
from services.notification_service.app.database import create_notification_document


class TestRiderDatabase:
    """Test MongoDB rider database operations"""

    def setup_method(self):
        """Reset database state before each test"""
        from services.rider_service.app.database import db
        db.client = None
        db.database = None

    @pytest.mark.asyncio
    @patch('services.rider_service.app.database.AsyncIOMotorClient')
    async def test_connect_to_mongo_success(self, mock_client):
        """Test successful MongoDB connection"""
        from services.rider_service.app.database import db

        try:
            # Reset database state
            db.client = None
            db.database = None

            mock_db_client = AsyncMock()
            mock_database = Mock()  # Use regular Mock instead of AsyncMock
            mock_admin = AsyncMock()

            mock_client.return_value = mock_db_client
            mock_db_client.get_database = Mock(return_value=mock_database)  # Make get_database synchronous
            mock_db_client.admin = mock_admin
            mock_admin.command = AsyncMock()

            await connect_to_mongo()

            assert db.client == mock_db_client
            # Check that get_database was called
            mock_db_client.get_database.assert_called_once_with("uber")
            mock_client.assert_called_once()
            mock_admin.command.assert_called_once_with('ping')
        finally:
            # Reset to clean state
            db.client = None
            db.database = None

    @pytest.mark.asyncio
    @patch('services.rider_service.app.database.AsyncIOMotorClient')
    async def test_connect_to_mongo_failure(self, mock_client):
        """Test MongoDB connection failure"""
        mock_client.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            await connect_to_mongo()

    @pytest.mark.asyncio
    async def test_close_mongo_connection(self):
        """Test closing MongoDB connection"""
        from services.rider_service.app.database import db
        # Save original client
        original_client = db.client

        try:
            # Set up test state
            mock_client = AsyncMock()
            mock_client.close = Mock()  # Make close synchronous
            db.client = mock_client

            await close_mongo_connection()

            mock_client.close.assert_called_once()
        finally:
            # Restore original client
            db.client = original_client
        # so we don't assert that here

    def test_get_database(self):
        """Test getting database instance"""
        from services.rider_service.app.database import db
        # Save original database
        original_database = db.database

        try:
            # Reset database state
            db.database = None
            mock_database = Mock()  # Use regular Mock instead of AsyncMock
            db.database = mock_database # type: ignore

            result = get_database()
            assert result == mock_database
        finally:
            # Restore original database
            db.database = original_database

    def test_create_rider_document(self):
        """Test creating rider document"""
        document = create_rider_document(
            rider_id="rider123",
            name="John Doe",
            email="john@example.com",
            phone="+4512345678",
            preferences={"language": "en", "notifications": True}
        )

        assert document["_id"] == "rider123"
        assert document["name"] == "John Doe"
        assert document["email"] == "john@example.com"
        assert document["phone"] == "+4512345678"
        assert document["preferences"] == {"language": "en", "notifications": True}
        assert "created_at" in document
        assert "updated_at" in document

    def test_create_rider_document_minimal(self):
        """Test creating rider document with minimal data"""
        document = create_rider_document(
            rider_id="rider456",
            name="Jane Smith",
            email="jane@example.com"
        )

        assert document["_id"] == "rider456"
        assert document["name"] == "Jane Smith"
        assert document["email"] == "jane@example.com"
        assert document["phone"] is None
        assert document["preferences"] == {}
        assert "created_at" in document
        assert "updated_at" in document


class TestNotificationDatabase:
    """Test MongoDB notification database operations"""

    def test_create_notification_document(self):
        """Test creating notification document"""
        document = create_notification_document(
            notification_id="notif123",
            user_id="user456",
            user_type="rider",
            notification_type="trip_assigned",
            title="Trip Assigned",
            message="Your driver is on the way!"
        )

        assert document["_id"] == "notif123"
        assert document["user_id"] == "user456"
        assert document["user_type"] == "rider"
        assert document["type"] == "trip_assigned"
        assert document["title"] == "Trip Assigned"
        assert document["message"] == "Your driver is on the way!"
        assert document["sent"] == False
        assert document["sent_at"] is None
        assert "created_at" in document
        assert "updated_at" in document

    def test_create_notification_document_different_types(self):
        """Test creating notification documents for different user types"""
        # Driver notification
        driver_doc = create_notification_document(
            notification_id="driver-notif",
            user_id="driver123",
            user_type="driver",
            notification_type="new_trip",
            title="New Trip Available",
            message="A new trip is available for pickup"
        )

        assert driver_doc["user_type"] == "driver"
        assert driver_doc["type"] == "new_trip"

        # Rider notification
        rider_doc = create_notification_document(
            notification_id="rider-notif",
            user_id="rider456",
            user_type="rider",
            notification_type="trip_completed",
            title="Trip Completed",
            message="Your trip has been completed successfully"
        )

        assert rider_doc["user_type"] == "rider"
        assert rider_doc["type"] == "trip_completed"


class TestMongoDBIntegration:
    """Integration tests for MongoDB operations"""

    @pytest.mark.asyncio
    async def test_full_rider_lifecycle(self):
        """Test complete rider lifecycle with MongoDB"""
        # This would require a real MongoDB connection
        # For now, we'll test the document creation logic
        document = create_rider_document(
            rider_id="test-rider",
            name="Test User",
            email="test@example.com"
        )

        # Verify document structure
        assert document["_id"] == "test-rider"
        assert document["name"] == "Test User"
        assert document["email"] == "test@example.com"
        from datetime import datetime
        assert isinstance(document["created_at"], datetime)
        assert isinstance(document["updated_at"], datetime)

    @pytest.mark.asyncio
    async def test_full_notification_lifecycle(self):
        """Test complete notification lifecycle with MongoDB"""
        # Test notification document creation
        document = create_notification_document(
            notification_id="test-notif",
            user_id="test-user",
            user_type="rider",
            notification_type="test",
            title="Test Notification",
            message="This is a test"
        )

        # Verify document structure
        assert document["_id"] == "test-notif"
        assert document["user_id"] == "test-user"
        assert document["sent"] == False
        assert document["sent_at"] is None

    def test_document_serialization(self):
        """Test that documents can be JSON serialized"""
        import json
        from datetime import datetime

        rider_doc = create_rider_document(
            rider_id="serial-test",
            name="Serial Test",
            email="serial@example.com"
        )

        # Custom JSON encoder for datetime objects
        def datetime_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat() + "Z"
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        # Should be JSON serializable with custom encoder
        json_str = json.dumps(rider_doc, default=datetime_encoder)
        parsed = json.loads(json_str)

        assert parsed["_id"] == "serial-test"
        assert parsed["name"] == "Serial Test"
        assert "created_at" in parsed
        assert "updated_at" in parsed

    def test_notification_types_coverage(self):
        """Test various notification types"""
        notification_types = [
            "trip_requested",
            "driver_assigned",
            "trip_started",
            "trip_completed",
            "payment_processed",
            "driver_arrived",
            "trip_cancelled"
        ]

        for notif_type in notification_types:
            doc = create_notification_document(
                notification_id=f"test-{notif_type}",
                user_id="test-user",
                user_type="rider",
                notification_type=notif_type,
                title=f"Test {notif_type}",
                message=f"Message for {notif_type}"
            )

            assert doc["type"] == notif_type
            assert doc["_id"] == f"test-{notif_type}"