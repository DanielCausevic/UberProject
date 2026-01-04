import pytest
from unittest.mock import patch, MagicMock
from services.trip_service.app.store import Trip, TripStore
from services.trip_service.app.schemas import CreateTripRequest, LatLng


class TestTripModel:
    """Test the Trip dataclass"""

    def test_trip_creation(self):
        """Test basic trip creation"""
        trip = Trip(
            id="test123",
            rider_id="rider456",
            pickup={"lat": 55.6761, "lng": 12.5683},
            dropoff={"lat": 55.6761, "lng": 12.5683}
        )

        assert trip.id == "test123"
        assert trip.rider_id == "rider456"
        assert trip.status == "REQUESTED"
        assert trip.assigned_driver_id is None
        assert trip.estimated_price_dkk is None
        assert trip.final_price_dkk is None

    def test_trip_with_all_fields(self):
        """Test trip with all fields populated"""
        trip = Trip(
            id="test123",
            rider_id="rider456",
            pickup={"lat": 55.6761, "lng": 12.5683},
            dropoff={"lat": 55.6761, "lng": 12.5683},
            status="ASSIGNED",
            assigned_driver_id="driver789",
            estimated_price_dkk=150.0,
            final_price_dkk=175.0
        )

        assert trip.status == "ASSIGNED"
        assert trip.assigned_driver_id == "driver789"
        assert trip.estimated_price_dkk == 150.0
        assert trip.final_price_dkk == 175.0


class TestTripStore:
    """Test the TripStore class"""

    @patch('services.trip_service.app.store.get_db')
    @patch('services.trip_service.app.store.create_tables')
    def test_trip_store_initialization(self, mock_create_tables, mock_get_db):
        """Test TripStore initialization"""
        store = TripStore()
        mock_create_tables.assert_called_once()

    @patch('services.trip_service.app.store.get_db')
    @patch('services.trip_service.app.store.create_tables')
    def test_create_trip(self, mock_create_tables, mock_get_db):
        """Test creating a new trip"""
        # Mock database session
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        # Mock database trip object
        mock_db_trip = MagicMock()
        mock_db_trip.id = "test123"
        mock_db_trip.rider_id = "rider456"
        mock_db_trip.pickup = '{"lat": 55.6761, "lng": 12.5683}'
        mock_db_trip.dropoff = '{"lat": 55.6761, "lng": 12.5683}'
        mock_db_trip.status = "REQUESTED"
        mock_db_trip.assigned_driver_id = None
        mock_db_trip.estimated_price_dkk = None
        mock_db_trip.final_price_dkk = None

        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        store = TripStore()
        trip = Trip(
            id="test123",
            rider_id="rider456",
            pickup={"lat": 55.6761, "lng": 12.5683},
            dropoff={"lat": 55.6761, "lng": 12.5683}
        )

        result = store.create(trip)

        assert result.id == "test123"
        assert result.rider_id == "rider456"
        assert result.pickup == {"lat": 55.6761, "lng": 12.5683}
        assert result.dropoff == {"lat": 55.6761, "lng": 12.5683}
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('services.trip_service.app.store.get_db')
    @patch('services.trip_service.app.store.create_tables')
    def test_get_trip_found(self, mock_create_tables, mock_get_db):
        """Test getting an existing trip"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_trip = MagicMock()
        mock_db_trip.configure_mock(**{
            'id': "test123",
            'rider_id': "rider456",
            'pickup': '{"lat": 55.6761, "lng": 12.5683}',
            'dropoff': '{"lat": 55.6761, "lng": 12.5683}',
            'status': "ASSIGNED",
            'assigned_driver_id': "driver789",
            'estimated_price_dkk': 150.0,
            'final_price_dkk': None
        })

        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_trip

        store = TripStore()
        result = store.get("test123")

        assert result is not None
        assert result.id == "test123"
        assert result.status == "ASSIGNED"
        assert result.assigned_driver_id == "driver789"
        assert result.estimated_price_dkk == 150.0

    @patch('services.trip_service.app.store.get_db')
    @patch('services.trip_service.app.store.create_tables')
    def test_get_trip_not_found(self, mock_create_tables, mock_get_db):
        """Test getting a non-existent trip"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_session.query.return_value.filter.return_value.first.return_value = None

        store = TripStore()
        result = store.get("nonexistent")

        assert result is None

    @patch('services.trip_service.app.store.get_db')
    @patch('services.trip_service.app.store.create_tables')
    def test_list_trips(self, mock_create_tables, mock_get_db):
        """Test listing all trips"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_trip = MagicMock()
        mock_db_trip.configure_mock(**{
            'id': "test123",
            'rider_id': "rider456",
            'pickup': '{"lat": 55.6761, "lng": 12.5683}',
            'dropoff': '{"lat": 55.6761, "lng": 12.5683}',
            'status': "REQUESTED",
            'assigned_driver_id': None,
            'estimated_price_dkk': None,
            'final_price_dkk': None
        })

        mock_session.query.return_value.all.return_value = [mock_db_trip]

        store = TripStore()
        result = store.list()

        assert len(result) == 1
        assert result[0].id == "test123"
        assert result[0].rider_id == "rider456"

    @patch('services.trip_service.app.store.get_db')
    @patch('services.trip_service.app.store.create_tables')
    def test_assign_driver(self, mock_create_tables, mock_get_db):
        """Test assigning a driver to a trip"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_trip = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_trip

        store = TripStore()
        store.assign_driver("trip123", "driver456")

        # Check that commit was called, indicating the method ran
        mock_session.commit.assert_called_once()

    @patch('services.trip_service.app.store.get_db')
    @patch('services.trip_service.app.store.create_tables')
    def test_assign_driver_not_found(self, mock_create_tables, mock_get_db):
        """Test assigning driver to non-existent trip"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_session.query.return_value.filter.return_value.first.return_value = None

        store = TripStore()

        with pytest.raises(KeyError):
            store.assign_driver("nonexistent", "driver456")

    @patch('services.trip_service.app.store.get_db')
    @patch('services.trip_service.app.store.create_tables')
    def test_set_estimate(self, mock_create_tables, mock_get_db):
        """Test setting price estimate"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_trip = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_trip

        store = TripStore()
        store.set_estimate("trip123", 150.0)

        mock_session.commit.assert_called_once()

    @patch('services.trip_service.app.store.get_db')
    @patch('services.trip_service.app.store.create_tables')
    def test_complete_trip(self, mock_create_tables, mock_get_db):
        """Test completing a trip"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_trip = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_trip

        store = TripStore()
        store.complete("trip123", 175.0)

        mock_session.commit.assert_called_once()


class TestSchemas:
    """Test Pydantic schemas"""

    def test_lat_lng_creation(self):
        """Test LatLng schema"""
        lat_lng = LatLng(lat=55.6761, lng=12.5683)
        assert lat_lng.lat == 55.6761
        assert lat_lng.lng == 12.5683

    def test_create_trip_request(self):
        """Test CreateTripRequest schema"""
        pickup = LatLng(lat=55.6761, lng=12.5683)
        dropoff = LatLng(lat=55.6761, lng=12.5683)

        request = CreateTripRequest(
            rider_id="rider123",
            pickup=pickup,
            dropoff=dropoff
        )

        assert request.rider_id == "rider123"
        assert request.pickup.lat == 55.6761
        assert request.dropoff.lng == 12.5683

    def test_create_trip_request_invalid_lat_lng(self):
        """Test CreateTripRequest with invalid coordinates"""
        with pytest.raises(ValueError):
            LatLng(lat=91, lng=12.5683)  # Invalid latitude

        with pytest.raises(ValueError):
            LatLng(lat=55.6761, lng=181)  # Invalid longitude