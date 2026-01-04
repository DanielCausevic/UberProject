from sqlalchemy import create_engine, String, Float, DateTime  # type: ignore
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker  # type: ignore
from typing import Optional
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@localhost:5432/uber")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    rider_id: Mapped[str] = mapped_column(String, nullable=False)
    pickup: Mapped[dict] = mapped_column(String, nullable=False)  # Store as JSON string
    dropoff: Mapped[dict] = mapped_column(String, nullable=False)  # Store as JSON string
    status: Mapped[str] = mapped_column(String, default="REQUESTED")
    assigned_driver_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    estimated_price_dkk: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    final_price_dkk: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
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