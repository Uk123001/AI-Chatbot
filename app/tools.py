"""
The three (+1 optional) tools required by the spec:
  1. RAG Tool            -> app.rag_pipeline.rag_tool
  2. Booking Persistence Tool -> booking_persistence_tool (below)
  3. Email Tool          -> email_tool (below)
  4. (Optional) Web Search Tool -> not implemented; out of scope for this build
"""
from typing import Optional

from app.database import get_session
from app.models import Customer, Booking
from app.email_utils import send_email
from app.config import settings


def booking_persistence_tool(payload: dict) -> dict:
    """
    Input: structured booking payload
        {name, email, phone, booking_type, date, time}
    Output: {success, booking_id} or {success: False, error}
    """
    required = ["name", "email", "phone", "booking_type", "date", "time"]
    missing = [f for f in required if not payload.get(f)]
    if missing:
        return {"success": False, "error": f"Missing fields: {', '.join(missing)}"}

    try:
        with get_session() as session:
            customer = (
                session.query(Customer)
                .filter(Customer.email == payload["email"])
                .first()
            )
            if not customer:
                customer = Customer(
                    name=payload["name"], email=payload["email"], phone=payload["phone"]
                )
                session.add(customer)
                session.flush()  # get customer_id before commit

            booking = Booking(
                customer_id=customer.customer_id,
                booking_type=payload["booking_type"],
                date=payload["date"],
                time=payload["time"],
                status="confirmed",
            )
            session.add(booking)
            session.flush()
            booking_id = booking.id

        return {"success": True, "booking_id": booking_id}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def email_tool(to_email: str, subject: str, body: str) -> dict:
    """Input: to_email/subject/body -> Output: {success, message}"""
    success, message = send_email(to_email, subject, body)
    return {"success": success, "message": message}


def build_confirmation_email(payload: dict, booking_id: int) -> tuple[str, str]:
    subject = f"Booking Confirmed - {settings.BUSINESS_NAME} (#{booking_id})"
    body = (
        f"Hi {payload['name']},\n\n"
        f"Your booking with {settings.BUSINESS_NAME} is confirmed. Here are the details:\n\n"
        f"  Booking ID:   {booking_id}\n"
        f"  Service:      {payload['booking_type']}\n"
        f"  Date:         {payload['date']}\n"
        f"  Time:         {payload['time']}\n"
        f"  Name:         {payload['name']}\n"
        f"  Phone:        {payload['phone']}\n\n"
        f"If you need to change or cancel this booking, just reply to this email "
        f"or contact us directly.\n\n"
        f"Thank you,\n{settings.BUSINESS_NAME}"
    )
    return subject, body
