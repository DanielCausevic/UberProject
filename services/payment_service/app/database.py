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

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    trip_id: Mapped[str] = mapped_column(String, nullable=False)
    rider_id: Mapped[str] = mapped_column(String, nullable=False)
    driver_id: Mapped[str] = mapped_column(String, nullable=False)
    amount_dkk: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="PENDING")  # PENDING, COMPLETED, FAILED, REFUNDED
    payment_method: Mapped[str] = mapped_column(String, nullable=False)
    transaction_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
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