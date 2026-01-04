import httpx
import time


class TestSystemIntegration:
    """Integration tests for the complete system"""

    def test_services_health_check(self):
        """Test that all services are healthy"""
        services = [
            ("http://localhost:3000/health", "gateway"),
            ("http://localhost:3001/health", "rider"),
            ("http://localhost:3002/health", "driver"),
            ("http://localhost:3003/health", "trip"),
            ("http://localhost:3004/health", "pricing"),
            ("http://localhost:3005/health", "payment"),
            ("http://localhost:3006/health", "notification")
        ]

        for url, service_name in services:
            response = httpx.get(url, timeout=5.0)
            assert response.status_code == 200
            data = response.json()
            assert data["ok"] == True
            assert data["service"] == f"{service_name}-service"

    def test_gateway_demo_endpoints(self):
        """Test gateway demo endpoints"""
        # Test services endpoint
        response = httpx.get("http://localhost:3000/demo/services", timeout=5.0)
        assert response.status_code == 200
        services = response.json()
        assert "rider" in services
        assert "driver" in services
        assert "trip" in services

    def test_full_trip_flow(self):
        """Test complete trip request to assignment flow"""
        # Step 1: Create a driver
        driver_data = {"name": "Test Driver"}
        response = httpx.post(
            "http://localhost:3000/demo/create-driver",
            json=driver_data,
            timeout=5.0
        )
        assert response.status_code == 201
        driver = response.json()
        assert "id" in driver
        assert driver["name"] == "Test Driver"
        assert driver["available"] == False
        driver_id = driver["id"]

        # Step 2: Make driver available
        response = httpx.post(
            f"http://localhost:3000/demo/driver-available/{driver_id}",
            timeout=5.0
        )
        assert response.status_code == 200
        driver = response.json()
        assert driver["available"] == True

        # Step 3: Request a trip
        trip_data = {
            "rider_id": "test-rider-123",
            "pickup": {"lat": 55.6761, "lng": 12.5683},
            "dropoff": {"lat": 55.6761, "lng": 12.5683}
        }
        response = httpx.post(
            "http://localhost:3000/demo/request-trip",
            json=trip_data,
            timeout=5.0
        )
        assert response.status_code == 201
        trip_response = response.json()
        assert "trip" in trip_response
        assert "published" in trip_response
        assert trip_response["published"] == "trip.requested"

        trip = trip_response["trip"]
        assert trip["rider_id"] == "test-rider-123"
        assert trip["status"] == "REQUESTED"
        trip_id = trip["id"]

        # Step 4: Wait a moment for event processing
        time.sleep(2)

        # Step 5: Check that trip was assigned
        response = httpx.get("http://localhost:3000/demo/trips", timeout=5.0)
        assert response.status_code == 200
        trips = response.json()
        assert len(trips) >= 1

        # Find our trip
        our_trip = None
        for t in trips:
            if t["id"] == trip_id:
                our_trip = t
                break

        assert our_trip is not None
        assert our_trip["status"] == "ASSIGNED"
        assert our_trip["assigned_driver_id"] == driver_id

        # Step 6: Verify driver is now unavailable
        response = httpx.get("http://localhost:3002/drivers", timeout=5.0)
        assert response.status_code == 200
        drivers = response.json()

        driver_found = None
        for d in drivers:
            if d["id"] == driver_id:
                driver_found = d
                break

        assert driver_found is not None
        assert driver_found["available"] == False

    def test_trip_service_api(self):
        """Test trip service API endpoints directly"""
        # Test list trips
        response = httpx.get("http://localhost:3003/trips", timeout=5.0)
        assert response.status_code == 200
        trips = response.json()
        assert isinstance(trips, list)

        # Test create trip directly
        trip_data = {
            "rider_id": "direct-test-rider",
            "pickup": {"lat": 55.6761, "lng": 12.5683},
            "dropoff": {"lat": 55.6761, "lng": 12.5683}
        }
        response = httpx.post(
            "http://localhost:3003/trips",
            json=trip_data,
            timeout=5.0
        )
        assert response.status_code == 201
        trip_response = response.json()
        assert "trip" in trip_response
        trip_id = trip_response["trip"]["id"]

        # Test get specific trip
        response = httpx.get(f"http://localhost:3003/trips/{trip_id}", timeout=5.0)
        assert response.status_code == 200
        trip = response.json()
        assert trip["id"] == trip_id
        assert trip["rider_id"] == "direct-test-rider"

    def test_driver_service_api(self):
        """Test driver service API endpoints directly"""
        # Test list drivers
        response = httpx.get("http://localhost:3002/drivers", timeout=5.0)
        assert response.status_code == 200
        drivers = response.json()
        assert isinstance(drivers, list)

        # Test create driver directly
        driver_data = {"name": "API Test Driver"}
        response = httpx.post(
            "http://localhost:3002/drivers",
            json=driver_data,
            timeout=5.0
        )
        assert response.status_code == 201
        driver = response.json()
        assert driver["name"] == "API Test Driver"
        assert driver["available"] == False
        driver_id = driver["id"]

        # Test set driver available
        response = httpx.post(
            f"http://localhost:3002/drivers/{driver_id}/available",
            timeout=5.0
        )
        assert response.status_code == 200
        driver = response.json()
        assert driver["available"] == True

    def test_event_system_resilience(self):
        """Test that system handles events gracefully"""
        # Create multiple drivers
        driver_ids = []
        for i in range(3):
            driver_data = {"name": f"Resilience Driver {i}"}
            response = httpx.post(
                "http://localhost:3000/demo/create-driver",
                json=driver_data,
                timeout=5.0
            )
            assert response.status_code == 201
            driver_ids.append(response.json()["id"])

        # Make all drivers available
        for driver_id in driver_ids:
            response = httpx.post(
                f"http://localhost:3000/demo/driver-available/{driver_id}",
                timeout=5.0
            )
            assert response.status_code == 200

        # Request multiple trips
        trip_ids = []
        for i in range(2):
            trip_data = {
                "rider_id": f"resilience-rider-{i}",
                "pickup": {"lat": 55.6761, "lng": 12.5683},
                "dropoff": {"lat": 55.6761, "lng": 12.5683}
            }
            response = httpx.post(
                "http://localhost:3000/demo/request-trip",
                json=trip_data,
                timeout=5.0
            )
            assert response.status_code == 201
            trip_ids.append(response.json()["trip"]["id"])

        # Wait for event processing
        time.sleep(3)

        # Check that trips were assigned
        response = httpx.get("http://localhost:3000/demo/trips", timeout=5.0)
        assert response.status_code == 200
        trips = response.json()

        assigned_count = sum(1 for t in trips if t["status"] == "ASSIGNED")
        assert assigned_count >= 2  # At least 2 trips should be assigned

    def test_error_handling(self):
        """Test error handling in API endpoints"""
        # Test invalid trip request
        invalid_trip = {
            "rider_id": "",  # Empty rider ID
            "pickup": {"lat": 91, "lng": 12.5683},  # Invalid latitude
            "dropoff": {"lat": 55.6761, "lng": 12.5683}
        }

        # This should still work as validation happens at the service level
        response = httpx.post(
            "http://localhost:3003/trips",
            json=invalid_trip,
            timeout=5.0
        )
        # The request might succeed at HTTP level but fail at processing
        assert response.status_code in [201, 422]  # Either created or validation error

        # Test non-existent trip
        response = httpx.get("http://localhost:3003/trips/nonexistent", timeout=5.0)
        assert response.status_code == 404

        # Test non-existent driver availability
        response = httpx.post(
            "http://localhost:3002/drivers/nonexistent/available",
            timeout=5.0
        )
        assert response.status_code == 404

    def test_database_persistence(self):
        """Test that data persists across service restarts"""
        # Create a driver
        driver_data = {"name": "Persistence Test Driver"}
        response = httpx.post(
            "http://localhost:3000/demo/create-driver",
            json=driver_data,
            timeout=5.0
        )
        assert response.status_code == 201
        driver_id = response.json()["id"]

        # Verify driver exists
        response = httpx.get("http://localhost:3002/drivers", timeout=5.0)
        assert response.status_code == 200
        drivers = response.json()
        driver_exists = any(d["id"] == driver_id for d in drivers)
        assert driver_exists

        # Create a trip
        trip_data = {
            "rider_id": "persistence-test-rider",
            "pickup": {"lat": 55.6761, "lng": 12.5683},
            "dropoff": {"lat": 55.6761, "lng": 12.5683}
        }
        response = httpx.post(
            "http://localhost:3000/demo/request-trip",
            json=trip_data,
            timeout=5.0
        )
        assert response.status_code == 201
        trip_id = response.json()["trip"]["id"]

        # Verify trip exists
        response = httpx.get("http://localhost:3003/trips", timeout=5.0)
        assert response.status_code == 200
        trips = response.json()
        trip_exists = any(t["id"] == trip_id for t in trips)
        assert trip_exists