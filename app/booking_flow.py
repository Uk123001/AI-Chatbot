"""
Conversational booking flow (slot filling + confirmation), matching the
required flow:

  1. Detect booking intent
  2. Extract known details
  3. Ask only for missing fields
  4. Use memory to avoid repeating questions
  5. Summarize details
  6. Ask explicit confirmation
  7. On confirmation: save to DB, send email
  8. Respond with booking ID
"""
import json
import re
from datetime import datetime
from typing import Optional

from dateutil import parser as date_parser

from app.llm import chat as llm_chat
from app.tools import booking_persistence_tool, email_tool, build_confirmation_email
from app.config import settings

FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]

FIELD_PROMPTS = {
    "name": "What name should I book this under?",
    "email": "What email address should I send the confirmation to?",
    "phone": "What's the best phone number to reach you on?",
    "booking_type": f"What would you like to book (e.g. a specific {settings.BOOKING_DOMAIN})?",
    "date": "What date works for you? (e.g. 2026-09-20 or 'next Friday')",
    "time": "What time would you like? (e.g. 14:30 or '2:30 PM')",
}

BOOKING_KEYWORDS = [
    "book", "booking", "appointment", "reserve", "reservation", "schedule",
    "slot", "table", "ticket", "enroll", "enrol", "sign up", "register",
    "class", "session",
]

CONFIRM_WORDS = {"yes", "y", "confirm", "correct", "yep", "yeah", "sure", "ok", "okay", "looks good", "go ahead"}
DENY_WORDS = {"no", "n", "cancel", "wrong", "nope", "change", "incorrect", "edit"}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-()]{7,}\d)")

EXTRACTION_SYSTEM_PROMPT = (
    "You extract booking details from a user's message. Respond with ONLY a "
    "compact JSON object (no prose, no markdown fences) with any of these keys "
    "that are clearly present in the message: name, email, phone, booking_type, "
    "date, time. Use null for anything not mentioned. Do not guess values that "
    "were not stated. Normalize date to YYYY-MM-DD and time to 24-hour HH:MM if "
    "you can confidently infer them, otherwise return the raw text the user gave."
)


def is_booking_intent(message: str, session: dict) -> bool:
    if session.get("booking_active"):
        return True
    lowered = message.lower()
    return any(kw in lowered for kw in BOOKING_KEYWORDS)


def _regex_extract(message: str) -> dict:
    found = {}
    email_match = EMAIL_RE.search(message)
    if email_match:
        found["email"] = email_match.group(0)
    phone_match = PHONE_RE.search(message)
    if phone_match:
        digits = re.sub(r"\D", "", phone_match.group(0))
        if len(digits) >= 7:
            found["phone"] = phone_match.group(0).strip()
    return found


def _llm_extract(message: str) -> dict:
    raw = llm_chat(EXTRACTION_SYSTEM_PROMPT, [], message)
    raw = raw.strip()
    # Strip accidental markdown fences
    raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        data = json.loads(raw)
        return {k: v for k, v in data.items() if v not in (None, "", "null")}
    except Exception:
        return {}


def extract_fields(message: str) -> dict:
    """Merge regex-based extraction (reliable for email/phone) with LLM extraction."""
    extracted = _llm_extract(message)
    extracted.update(_regex_extract(message))  # regex wins for email/phone
    return extracted


def validate_field(field: str, value: str) -> tuple[Optional[str], Optional[str]]:
    """Returns (normalized_value, error_message)."""
    value = str(value).strip()
    if field == "email":
        if not EMAIL_RE.fullmatch(value):
            return None, "That doesn't look like a valid email address. Could you re-enter it?"
        return value, None

    if field == "phone":
        digits = re.sub(r"\D", "", value)
        if len(digits) < 7:
            return None, "That phone number looks too short. Could you re-enter it?"
        return value, None

    if field == "date":
        try:
            parsed = date_parser.parse(value, fuzzy=True, default=datetime.now())
            return parsed.strftime("%Y-%m-%d"), None
        except Exception:
            return None, "I couldn't understand that date. Please use a format like YYYY-MM-DD."

    if field == "time":
        try:
            parsed = date_parser.parse(value, fuzzy=True, default=datetime.now())
            return parsed.strftime("%H:%M"), None
        except Exception:
            return None, "I couldn't understand that time. Please use a format like 14:30 or 2:30 PM."

    if field in ("name", "booking_type"):
        if len(value) < 1:
            return None, f"Could you tell me the {field.replace('_', ' ')}?"
        return value, None

    return value, None


def _new_draft() -> dict:
    return {field: None for field in FIELDS}


def summarize(draft: dict) -> str:
    return (
        f"Here's what I have:\n"
        f"  • Name: {draft['name']}\n"
        f"  • Email: {draft['email']}\n"
        f"  • Phone: {draft['phone']}\n"
        f"  • Booking: {draft['booking_type']}\n"
        f"  • Date: {draft['date']}\n"
        f"  • Time: {draft['time']}\n\n"
        f"Shall I confirm this booking? (yes/no)"
    )


def process(session: dict, message: str) -> str:
    """
    Mutates `session` in place (booking_active, draft, awaiting_confirmation)
    and returns the assistant's reply text. `session` also gets `booking_id`
    set when a booking is completed this turn (read by the caller).
    """
    if not session.get("draft"):
        session["draft"] = _new_draft()
    session["booking_active"] = True
    session["booking_id"] = None

    draft = session["draft"]
    lowered = message.strip().lower()

    # --- Confirmation stage ---
    if session.get("awaiting_confirmation"):
        if any(w in lowered for w in CONFIRM_WORDS) and lowered not in DENY_WORDS:
            result = booking_persistence_tool(draft)
            if not result["success"]:
                return f"I couldn't save the booking ({result['error']}). Let's try again — {FIELD_PROMPTS['name']}"

            booking_id = result["booking_id"]
            session["booking_id"] = booking_id

            subject, body = build_confirmation_email(draft, booking_id)
            email_result = email_tool(draft["email"], subject, body)

            # Reset the flow
            session["booking_active"] = False
            session["awaiting_confirmation"] = False
            session["draft"] = _new_draft()

            reply = (
                f"You're all set! Your booking is confirmed with ID #{booking_id}."
            )
            if email_result["success"]:
                reply += " A confirmation email is on its way."
            else:
                reply += f" (Note: the confirmation email could not be sent — {email_result['message']})"
            return reply

        if any(w in lowered for w in DENY_WORDS):
            session["awaiting_confirmation"] = False
            return "No problem — what would you like to change? Tell me the corrected detail."

        return "Sorry, should I go ahead and confirm this booking? (yes/no)"

    # --- Collection stage ---
    extracted = extract_fields(message)
    errors = []
    for field, value in extracted.items():
        if field in FIELDS and value:
            normalized, error = validate_field(field, value)
            if error:
                errors.append(error)
            else:
                draft[field] = normalized

    if errors:
        return " ".join(errors)

    missing = next((f for f in FIELDS if not draft.get(f)), None)
    if missing:
        return FIELD_PROMPTS[missing]

    session["awaiting_confirmation"] = True
    return summarize(draft)
