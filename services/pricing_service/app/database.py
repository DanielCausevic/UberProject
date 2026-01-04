from sqlalchemy import create_engine, String, Float, DateTime, Boolean  # type: ignore
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker  # type: ignore
import redis
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@localhost:5432/uber")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# PostgreSQL setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class PricingRule(Base):
    __tablename__ = "pricing_rules"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    base_fare: Mapped[float] = mapped_column(Float, nullable=False)
    per_km_rate: Mapped[float] = mapped_column(Float, nullable=False)
    per_minute_rate: Mapped[float] = mapped_column(Float, nullable=False)
    minimum_fare: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

# Redis setup
redis_client = None

def get_redis():
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL)
    return redis_client

def cache_pricing_rule(rule_id: str, rule_data: dict, ttl_seconds: int = 3600):
    """Cache pricing rule in Redis"""
    try:
        redis_conn = get_redis()
        key = f"pricing_rule:{rule_id}"
        redis_conn.setex(key, ttl_seconds, str(rule_data))
    except Exception:
        # Graceful degradation - ignore cache errors
        pass

def get_cached_pricing_rule(rule_id: str) -> dict:
    """Get cached pricing rule from Redis"""
    try:
        redis_conn = get_redis()
        key = f"pricing_rule:{rule_id}"
        cached_data = redis_conn.get(key)
        if cached_data:
            try:
                return eval(cached_data)  # Note: In production, use JSON serialization
            except (SyntaxError, ValueError):
                return None
        return None
    except Exception:
        # Graceful degradation - return None on cache errors
        return None

def invalidate_pricing_cache(rule_id: str):
    """Invalidate cached pricing rule"""
    redis_conn = get_redis()
    key = f"pricing_rule:{rule_id}"
    redis_conn.delete(key)