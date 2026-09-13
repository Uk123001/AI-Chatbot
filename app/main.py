"""
AI Booking Assistant - FastAPI backend.

Routes:
  POST   /api/chat              conversational endpoint (RAG + booking flow)
  POST   /api/upload             upload a PDF to index into the RAG store
  GET    /api/bookings           admin: list bookings (filter by name/email/date)
  GET    /api/bookings/export    admin: export bookings as CSV
  DELETE /api/bookings/{id}      admin: cancel a booking
  GET    /api/health             health/status check

Static frontend is served at "/" (chat) and "/admin" (dashboard).
"""
import csv
import io
import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db, get_session
from app.models import Customer, Booking
from app.schemas import ChatRequest, ChatResponse, UploadResponse, HealthResponse
from app.chat_logic import handle_message
from app.rag_pipeline import ingest_pdf, store as vector_store
from app.llm import active_provider_name

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

app = FastAPI(title="AI Booking Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


def _check_admin(x_admin_key: str = Header(default="")):
    if x_admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key.")


# ---------------------------------------------------------------- Chat -----
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    result = handle_message(req.session_id, req.message)
    return ChatResponse(session_id=req.session_id, **result)


# -------------------------------------------------------------- Upload -----
@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    try:
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        chunks = ingest_pdf(dest_path, file.filename)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {exc}")

    return UploadResponse(
        filename=file.filename,
        chunks_indexed=chunks,
        message=f"Indexed {chunks} chunks from {file.filename}. Ask me anything about it!",
    )


# --------------------------------------------------------- Admin: list -----
@app.get("/api/bookings")
def list_bookings(
    search: str = Query(default=""),
    date: str = Query(default=""),
    x_admin_key: str = Header(default=""),
):
    _check_admin(x_admin_key)
    with get_session() as session:
        query = session.query(Booking, Customer).join(Customer, Booking.customer_id == Customer.customer_id)
        if search:
            like = f"%{search.lower()}%"
            query = query.filter(
                (Customer.name.ilike(like)) | (Customer.email.ilike(like))
            )
        if date:
            query = query.filter(Booking.date == date)

        rows = query.order_by(Booking.created_at.desc()).all()
        return [
            {
                "id": b.id,
                "customer_id": c.customer_id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "booking_type": b.booking_type,
                "date": b.date,
                "time": b.time,
                "status": b.status,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b, c in rows
        ]


# ------------------------------------------------------- Admin: export -----
@app.get("/api/bookings/export")
def export_bookings(x_admin_key: str = Header(default="")):
    _check_admin(x_admin_key)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "email", "phone", "booking_type", "date", "time", "status", "created_at"])

    with get_session() as session:
        rows = (
            session.query(Booking, Customer)
            .join(Customer, Booking.customer_id == Customer.customer_id)
            .order_by(Booking.created_at.desc())
            .all()
        )
        for b, c in rows:
            writer.writerow(
                [b.id, c.name, c.email, c.phone, b.booking_type, b.date, b.time, b.status, b.created_at]
            )
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bookings.csv"},
    )


# ------------------------------------------------------- Admin: cancel -----
@app.delete("/api/bookings/{booking_id}")
def cancel_booking(booking_id: int, x_admin_key: str = Header(default="")):
    _check_admin(x_admin_key)
    with get_session() as session:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found.")
        booking.status = "cancelled"
    return {"success": True}


# ------------------------------------------------------------- Health -----
@app.get("/api/health", response_model=HealthResponse)
def health():
    try:
        provider = active_provider_name()
    except Exception:
        provider = "none"
    return HealthResponse(status="ok", llm_provider=provider, documents_indexed=len(set(vector_store.sources)))


# --------------------------------------------------------- Frontend -----
app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/admin")
def serve_admin():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))
