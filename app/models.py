"""
ORM models matching the schema in the problem statement:

customers: customer_id (PK), name, email, phone
bookings:  id (PK), customer_id (FK), booking_type, date, time, status, created_at
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)

    bookings = relationship("Booking", back_populates="customer")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    booking_type = Column(String, nullable=False)
    date = Column(String, nullable=False)   # YYYY-MM-DD
    time = Column(String, nullable=False)   # HH:MM
    status = Column(String, nullable=False, default="confirmed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="bookings")
