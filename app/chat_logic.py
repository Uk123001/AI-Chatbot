"""
Top-level chat orchestration: maintains short-term memory per session and
routes each message to either the booking flow or general/RAG conversation.
"""
import threading
from typing import Dict

from app.config import settings
from app.llm import chat as llm_chat
from app.rag_pipeline import rag_tool, store as vector_store
from app.booking_flow import is_booking_intent, process as run_booking_flow

_LOCK = threading.Lock()
_SESSIONS: Dict[str, dict] = {}

GENERAL_SYSTEM_PROMPT = (
    f"You are the AI assistant for {settings.BUSINESS_NAME}, which handles "
    f"{settings.BOOKING_DOMAIN} bookings. Be warm, concise, and helpful. "
    "If the user wants to book, reserve, or schedule something, let them know "
    "you can help them do that right in the chat. If they ask about uploaded "
    "documents, answer from those documents only."
)


def _get_session(session_id: str) -> dict:
    with _LOCK:
        if session_id not in _SESSIONS:
            _SESSIONS[session_id] = {
                "history": [],
                "booking_active": False,
                "awaiting_confirmation": False,
                "draft": None,
                "booking_id": None,
            }
        return _SESSIONS[session_id]


def _trim_history(session: dict):
    max_len = settings.MAX_HISTORY_MESSAGES
    if len(session["history"]) > max_len:
        session["history"] = session["history"][-max_len:]


def handle_message(session_id: str, message: str) -> dict:
    """
    Returns {"reply": str, "booking_id": int|None, "stage": str}
    """
    session = _get_session(session_id)
    session["history"].append({"role": "user", "content": message})

    if is_booking_intent(message, session):
        reply = run_booking_flow(session, message)
        stage = "booked" if session.get("booking_id") else (
            "confirming" if session.get("awaiting_confirmation") else "collecting"
        )
    else:
        if not vector_store.is_empty():
            reply = rag_tool(message, session["history"])
        else:
            reply = llm_chat(GENERAL_SYSTEM_PROMPT, session["history"], message)
        stage = "general"

    session["history"].append({"role": "assistant", "content": reply})
    _trim_history(session)

    return {
        "reply": reply,
        "booking_id": session.get("booking_id"),
        "stage": stage,
    }
