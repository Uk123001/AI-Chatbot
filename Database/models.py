from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import config

Base = declarative_base()


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    customer_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    bookings = relationship("Booking", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(id={self.customer_id}, name={self.name}, email={self.email})>"


class Booking(Base):
    """Booking model"""
    __tablename__ = "bookings"
    
    booking_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    booking_type = Column(String(100), nullable=False)  # doctor, salon, hotel, events, classes, etc.
    booking_date = Column(String(20), nullable=False)  # YYYY-MM-DD format
    booking_time = Column(String(10), nullable=False)  # HH:MM format
    status = Column(String(50), default="confirmed")  # confirmed, pending, cancelled
    additional_details = Column(String(500))  # Any extra info
    created_at = Column(DateTime, default=datetime.utcnow)
    email_sent = Column(Integer, default=0)  # 0 or 1 boolean flag
    
    # Relationship
    customer = relationship("Customer", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.booking_id}, customer_id={self.customer_id}, type={self.booking_type}, status={self.status})>"


def init_db():
    """Initialize database"""
    engine = create_engine(config.DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session"""
    engine = create_engine(config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()
