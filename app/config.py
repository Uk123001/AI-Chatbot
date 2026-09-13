"""
Central configuration for the AI Booking Assistant.
All values are read from environment variables (see .env.example).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- LLM providers ---
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq").lower()  # groq | openai | gemini

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # --- Database ---
    # Defaults to local SQLite. Set DATABASE_URL to a Postgres/Supabase URL for
    # real persistence on platforms with an ephemeral filesystem.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/booking.db")

    # --- Email (SMTP) ---
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", os.getenv("SMTP_USER", ""))
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "true").lower() == "true"

    # --- Admin dashboard ---
    ADMIN_KEY: str = os.getenv("ADMIN_KEY", "admin123")

    # --- Business identity (shown in chat + emails) ---
    BUSINESS_NAME: str = os.getenv("BUSINESS_NAME", "Aster Appointments")
    BOOKING_DOMAIN: str = os.getenv("BOOKING_DOMAIN", "general services")

    # --- Memory ---
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "25"))

    # --- CORS ---
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # --- Uploads ---
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploads")


settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("./data", exist_ok=True)
