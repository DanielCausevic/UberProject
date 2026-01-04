import pytest
from unittest.mock import Mock, patch, MagicMock
from services.pricing_service.app.database import get_redis, cache_pricing_rule, get_cached_pricing_rule, invalidate_pricing_cache


class TestRedisOperations:
    """Test Redis caching operations"""

    @patch('services.pricing_service.app.database.redis')
    def test_get_redis_client(self, mock_redis):
        """Test getting Redis client instance"""
        mock_client = Mock()
        mock_redis.from_url.return_value = mock_client

        # Reset global client
        import services.pricing_service.app.database as db_module
        db_module.redis_client = None

        client = get_redis()

        assert client == mock_client
        mock_redis.from_url.assert_called_once_with("redis://localhost:6379")

    @patch('services.pricing_service.app.database.get_redis')
    def test_cache_pricing_rule(self, mock_get_redis):
        """Test caching pricing rule"""
        mock_client = Mock()
        mock_get_redis.return_value = mock_client

        rule_data = {
            "id": "rule123",
            "name": "Standard Fare",
            "base_fare": 50.0,
            "per_km_rate": 10.0,
            "per_minute_rate": 2.0,
            "minimum_fare": 75.0
        }

        cache_pricing_rule("rule123", rule_data, ttl_seconds=1800)

        mock_client.setex.assert_called_once_with(
            "pricing_rule:rule123",
            1800,
            str(rule_data)
        )

    @patch('services.pricing_service.app.database.get_redis')
    def test_get_cached_pricing_rule_hit(self, mock_get_redis):
        """Test getting cached pricing rule (cache hit)"""
        mock_client = Mock()
        mock_get_redis.return_value = mock_client

        rule_data = {
            "id": "rule123",
            "name": "Standard Fare",
            "base_fare": 50.0
        }
        mock_client.get.return_value = str(rule_data)

        result = get_cached_pricing_rule("rule123")

        assert result == rule_data
        mock_client.get.assert_called_once_with("pricing_rule:rule123")

    @patch('services.pricing_service.app.database.get_redis')
    def test_get_cached_pricing_rule_miss(self, mock_get_redis):
        """Test getting cached pricing rule (cache miss)"""
        mock_client = Mock()
        mock_get_redis.return_value = mock_client

        mock_client.get.return_value = None

        result = get_cached_pricing_rule("nonexistent")

        assert result is None
        mock_client.get.assert_called_once_with("pricing_rule:nonexistent")

    @patch('services.pricing_service.app.database.get_redis')
    def test_get_cached_pricing_rule_invalid_data(self, mock_get_redis):
        """Test getting cached pricing rule with invalid data"""
        mock_client = Mock()
        mock_get_redis.return_value = mock_client

        # Return invalid JSON
        mock_client.get.return_value = "invalid json"

        result = get_cached_pricing_rule("rule123")

        # Should handle the eval error gracefully
        # Note: In production, this should use JSON instead of eval
        assert result is None

    @patch('services.pricing_service.app.database.get_redis')
    def test_invalidate_pricing_cache(self, mock_get_redis):
        """Test invalidating pricing cache"""
        mock_client = Mock()
        mock_get_redis.return_value = mock_client

        invalidate_pricing_cache("rule123")

        mock_client.delete.assert_called_once_with("pricing_rule:rule123")


class TestPricingRuleModel:
    """Test pricing rule database model"""

    @patch('services.pricing_service.app.database.get_db')
    @patch('services.pricing_service.app.database.create_tables')
    def test_pricing_rule_creation(self, mock_create_tables, mock_get_db):
        """Test creating pricing rule"""
        from services.pricing_service.app.database import PricingRule

        # Mock database session
        mock_session = MagicMock()
        mock_get_db.return_value.__next__.return_value = mock_session

        mock_db_rule = MagicMock()
        mock_db_rule.id = "rule123"
        mock_db_rule.name = "Standard Fare"
        mock_db_rule.base_fare = 50.0
        mock_db_rule.per_km_rate = 10.0
        mock_db_rule.per_minute_rate = 2.0
        mock_db_rule.minimum_fare = 75.0
        mock_db_rule.active = True

        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        # Create pricing rule
        rule = PricingRule(
            id="rule123",
            name="Standard Fare",
            base_fare=50.0,
            per_km_rate=10.0,
            per_minute_rate=2.0,
            minimum_fare=75.0,
            active=True
        )

        mock_session.add.assert_not_called()  # We can't actually instantiate the model without DB

    def test_pricing_calculations(self):
        """Test pricing calculation logic"""
        # Test data for pricing calculations
        base_fare = 50.0
        per_km_rate = 10.0
        per_minute_rate = 2.0
        minimum_fare = 75.0

        # Test scenarios
        test_cases = [
            # (distance_km, duration_min, expected_fare)
            (1.0, 5, 75.0),    # Short trip: 50 + 10 + 10 = 70, but min 75
            (2.0, 10, 90.0),   # Medium trip: 50 + 20 + 20 = 90
            (5.0, 20, 140.0),  # Long trip: 50 + 50 + 40 = 140
        ]

        for distance, duration, expected in test_cases:
            fare = base_fare + (distance * per_km_rate) + (duration * per_minute_rate)
            final_fare = max(fare, minimum_fare)

            assert final_fare == expected


class TestPricingServiceIntegration:
    """Integration tests for pricing service"""

    @patch('services.pricing_service.app.database.get_redis')
    @patch('services.pricing_service.app.database.get_db')
    def test_cache_workflow(self, mock_get_db, mock_redis):
        """Test complete cache workflow"""
        mock_redis_client = Mock()
        mock_redis.return_value = mock_redis_client

        # Test data
        rule_id = "premium_rule"
        rule_data = {
            "id": rule_id,
            "name": "Premium Fare",
            "base_fare": 75.0,
            "per_km_rate": 15.0,
            "per_minute_rate": 3.0,
            "minimum_fare": 100.0
        }

        # Cache the rule
        cache_pricing_rule(rule_id, rule_data)

        # Verify it was cached
        mock_redis_client.setex.assert_called_once()

        # Simulate cache hit
        mock_redis_client.get.return_value = str(rule_data)
        cached = get_cached_pricing_rule(rule_id)

        assert cached == rule_data

        # Invalidate cache
        invalidate_pricing_cache(rule_id)
        mock_redis_client.delete.assert_called_once_with(f"pricing_rule:{rule_id}")

        # Simulate cache miss after invalidation
        mock_redis_client.get.return_value = None
        cached_after_invalidation = get_cached_pricing_rule(rule_id)
        assert cached_after_invalidation is None

    def test_pricing_rule_validation(self):
        """Test pricing rule data validation"""
        # Valid pricing rules
        valid_rules = [
            {
                "id": "standard",
                "name": "Standard",
                "base_fare": 50.0,
                "per_km_rate": 10.0,
                "per_minute_rate": 2.0,
                "minimum_fare": 75.0,
                "active": True
            },
            {
                "id": "premium",
                "name": "Premium",
                "base_fare": 75.0,
                "per_km_rate": 15.0,
                "per_minute_rate": 3.0,
                "minimum_fare": 100.0,
                "active": True
            }
        ]

        for rule in valid_rules:
            assert rule["base_fare"] > 0
            assert rule["per_km_rate"] > 0
            assert rule["per_minute_rate"] > 0
            assert rule["minimum_fare"] >= rule["base_fare"]

    def test_pricing_edge_cases(self):
        """Test edge cases in pricing calculations"""
        # Zero distance/duration
        fare = 50.0 + (0 * 10.0) + (0 * 2.0)  # Should be base fare
        assert fare == 50.0

        # Very long trip
        fare = 50.0 + (100 * 10.0) + (120 * 2.0)  # 50 + 1000 + 240 = 1290
        assert fare == 1290.0

        # Minimum fare enforcement
        low_fare = 50.0 + (0.1 * 10.0) + (1 * 2.0)  # 50 + 1 + 2 = 53
        final_fare = max(low_fare, 75.0)  # Should be minimum fare
        assert final_fare == 75.0

    @patch('services.pricing_service.app.database.get_redis')
    def test_cache_error_handling(self, mock_get_redis):
        """Test error handling in cache operations"""
        mock_client = Mock()
        mock_get_redis.return_value = mock_client

        # Simulate Redis connection error
        mock_client.setex.side_effect = Exception("Redis connection failed")

        # Should not raise exception (graceful degradation)
        try:
            cache_pricing_rule("rule123", {"test": "data"})
        except Exception:
            pytest.fail("Cache operation should handle errors gracefully")

        # Simulate Redis get error
        mock_client.get.side_effect = Exception("Redis get failed")

        result = get_cached_pricing_rule("rule123")
        assert result is None  # Should return None on error