import pytest
from unittest.mock import patch, MagicMock, Mock
from services.driver_service.app.store import Driver, DriverStore
from services.driver_service.app.schemas import CreateDriverRequest


class TestDriverModel:
    """Test the Driver dataclass"""

    def test_driver_creation(self):
        """Test basic driver creation"""
        driver = Driver(id="driver123", name="John Doe")

        assert driver.id == "driver123"
        assert driver.name == "John Doe"
        assert driver.available == False  # Default value

    def test_driver_with_availability(self):
        """Test driver with explicit availability"""
        driver = Driver(id="driver123", name="John Doe", available=True)

        assert driver.id == "driver123"
        assert driver.name == "John Doe"
        assert driver.available == True


class TestDriverStore:
    """Test the DriverStore class"""

    @patch('services.driver_service.app.store.get_db')
    @patch('services.driver_service.app.store.create_tables')
    def test_driver_store_initialization(self, mock_create_tables, mock_get_db):
        """Test DriverStore initialization"""
        store = DriverStore()
        mock_create_tables.assert_called_once()

    @patch('services.driver_service.app.store.get_db')
    @patch('services.driver_service.app.store.create_tables')
    def test_create_driver(self, mock_create_tables, mock_get_db):
        """Test creating a new driver"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_driver = MagicMock()
        mock_db_driver.id = "driver123"
        mock_db_driver.name = "John Doe"
        mock_db_driver.available = False

        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        store = DriverStore()
        driver = Driver(id="driver123", name="John Doe")

        result = store.create(driver)

        assert result.id == "driver123"
        assert result.name == "John Doe"
        assert result.available == False
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('services.driver_service.app.store.get_db')
    @patch('services.driver_service.app.store.create_tables')
    def test_get_driver_found(self, mock_create_tables, mock_get_db):
        """Test getting an existing driver"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_driver = MagicMock()
        mock_db_driver.id = "driver123"
        mock_db_driver.name = "John Doe"
        mock_db_driver.available = True

        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_driver

        store = DriverStore()
        result = store.get("driver123")

        assert result is not None

    @patch('services.driver_service.app.store.get_db')
    @patch('services.driver_service.app.store.create_tables')
    def test_get_driver_not_found(self, mock_create_tables, mock_get_db):
        """Test getting a non-existent driver"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_session.query.return_value.filter.return_value.first.return_value = None

        store = DriverStore()
        result = store.get("nonexistent")

        assert result is None

    @patch('services.driver_service.app.store.get_db')
    @patch('services.driver_service.app.store.create_tables')
    def test_list_drivers(self, mock_create_tables, mock_get_db):
        """Test listing all drivers"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_driver1 = MagicMock()
        mock_db_driver1.id = "driver1"
        mock_db_driver1.name = "John Doe"
        mock_db_driver1.available = True

        mock_db_driver2 = MagicMock()
        mock_db_driver2.id = "driver2"
        mock_db_driver2.name = "Jane Smith"
        mock_db_driver2.available = False

        mock_session.query.return_value = Mock(all=Mock(return_value=[mock_db_driver1, mock_db_driver2]))

        store = DriverStore()
        result = store.list()

        assert len(result) == 2

    @patch('services.driver_service.app.store.get_db')
    @patch('services.driver_service.app.store.create_tables')
    def test_pick_available_driver_found(self, mock_create_tables, mock_get_db):
        """Test picking an available driver"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_driver = MagicMock()
        mock_db_driver.id = "driver123"
        mock_db_driver.name = "John Doe"
        mock_db_driver.available = True

        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_driver

        store = DriverStore()
        result = store.pick_available()

        assert result is not None

    @patch('services.driver_service.app.store.get_db')
    @patch('services.driver_service.app.store.create_tables')
    def test_pick_available_driver_none_available(self, mock_create_tables, mock_get_db):
        """Test picking driver when none are available"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_session.query.return_value.filter.return_value.first.return_value = None

        store = DriverStore()
        result = store.pick_available()

        assert result is None

    @patch('services.driver_service.app.store.get_db')
    @patch('services.driver_service.app.store.create_tables')
    def test_set_available_success(self, mock_create_tables, mock_get_db):
        """Test setting driver availability successfully"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_driver = MagicMock()
        mock_db_driver.id = "driver123"
        mock_db_driver.name = "John Doe"
        mock_db_driver.available = False

        mock_session.query.return_value.filter.return_value.first.return_value = mock_db_driver

        store = DriverStore()
        store.set_available("driver123", True)

        mock_session.commit.assert_called_once()

    @patch('services.driver_service.app.store.get_db')
    @patch('services.driver_service.app.store.create_tables')
    def test_set_available_not_found(self, mock_create_tables, mock_get_db):
        """Test setting availability for non-existent driver"""
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session  # For context manager
        mock_session.__exit__.return_value = None
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_session.query.return_value.filter.return_value.first.return_value = None

        store = DriverStore()

        with pytest.raises(KeyError):
            store.set_available("nonexistent", True)


class TestSchemas:
    """Test Pydantic schemas"""

    def test_create_driver_request(self):
        """Test CreateDriverRequest schema"""
        request = CreateDriverRequest(name="John Doe")

        assert request.name == "John Doe"

    def test_create_driver_request_empty_name(self):
        """Test CreateDriverRequest with empty name"""
        with pytest.raises(ValueError):
            CreateDriverRequest(name="")

    def test_create_driver_request_long_name(self):
        """Test CreateDriverRequest with very long name"""
        long_name = "A" * 1000
        request = CreateDriverRequest(name=long_name)
        assert request.name == long_name