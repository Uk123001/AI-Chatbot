"""Pydantic schemas for API requests/responses."""
from typing import Optional, List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    booking_id: Optional[int] = None
    stage: Optional[str] = None  # "general" | "collecting" | "confirming" | "booked"


class BookingOut(BaseModel):
    id: int
    customer_id: int
    name: str
    email: str
    phone: str
    booking_type: str
    date: str
    time: str
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    message: str


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    documents_indexed: int
