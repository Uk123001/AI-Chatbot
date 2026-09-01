"""
Constants and enums used throughout the application
"""

# ============================================
# Booking Types
# ============================================
BOOKING_TYPES = [
    "doctor",
    "salon",
    "hotel",
    "events",
    "classes",
    "restaurant",
    "gym",
    "spa",
    "beauty",
    "fitness",
    "consultation",
    "appointment"
]

BOOKING_TYPE_EMOJIS = {
    "doctor": "👨‍⚕️",
    "salon": "💇",
    "hotel": "🏨",
    "events": "🎉",
    "classes": "📚",
    "restaurant": "🍽️",
    "gym": "💪",
    "spa": "🧖",
    "beauty": "💄",
    "fitness": "🏃",
    "consultation": "💼",
    "appointment": "📅"
}

# ============================================
# Booking Status
# ============================================
BOOKING_STATUS = {
    "CONFIRMED": "confirmed",
    "PENDING": "pending",
    "CANCELLED": "cancelled",
    "COMPLETED": "completed"
}

# ============================================
# Chat Intent Types
# ============================================
INTENT_TYPES = {
    "BOOKING": "booking",
    "GENERAL": "general",
    "CONFIRMATION": "confirmation",
    "CANCELLATION": "cancellation"
}

# ============================================
# Booking Flow States
# ============================================
BOOKING_STATES = {
    "START": "start",
    "DETECT_INTENT": "booking_detected",
    "COLLECT_NAME": "collect_name",
    "COLLECT_EMAIL": "collect_email",
    "COLLECT_PHONE": "collect_phone",
    "COLLECT_TYPE": "collect_type",
    "COLLECT_DATE": "collect_date",
    "COLLECT_TIME": "collect_time",
    "SUMMARIZE": "summarize",
    "CONFIRM": "confirm",
    "COMPLETED": "completed"
}

# ============================================
# Validation Patterns
# ============================================
VALIDATION_PATTERNS = {
    "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "phone": r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
    "date": r'^(\d{4})-(\d{2})-(\d{2})$',
    "time": r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$'
}

# ============================================
# Error Messages
# ============================================
ERROR_MESSAGES = {
    "INVALID_EMAIL": "Please provide a valid email address (e.g., user@example.com)",
    "INVALID_PHONE": "Please provide a valid phone number",
    "INVALID_DATE": "Please provide a date in YYYY-MM-DD format",
    "INVALID_TIME": "Please provide a time in HH:MM format (24-hour)",
    "MISSING_FIELD": "Please provide all required information",
    "DB_ERROR": "Unable to save booking. Please try again.",
    "EMAIL_ERROR": "Email could not be sent, but booking was saved.",
    "API_ERROR": "Unable to process request. Please try again.",
}

# ============================================
# Success Messages
# ============================================
SUCCESS_MESSAGES = {
    "BOOKING_SAVED": "Booking saved successfully!",
    "EMAIL_SENT": "Confirmation email sent!",
    "PDF_UPLOADED": "PDF uploaded and processed successfully!",
    "BOOKING_CONFIRMED": "Your booking has been confirmed."
}

# ============================================
# Prompts and Questions
# ============================================
BOOKING_QUESTIONS = {
    "name": "What is your name?",
    "email": "What is your email address?",
    "phone": "What is your phone number?",
    "type": "What type of booking are you looking for? (e.g., doctor, salon, hotel, events, classes)",
    "date": "What date would you prefer? (Please use YYYY-MM-DD format)",
    "time": "What time would you prefer? (Please use HH:MM format in 24-hour)",
    "confirm": "Please confirm your booking details. Say 'yes' to confirm or 'no' to make changes."
}

# ============================================
# Email Templates
# ============================================
EMAIL_SUBJECT_TEMPLATE = "Booking Confirmation - #{booking_id}"

EMAIL_BODY_TEMPLATE = """
Dear {name},

Thank you for your booking! Here are your confirmation details:

Booking ID: {booking_id}
Service Type: {booking_type}
Date: {date}
Time: {time}
Email: {email}
Phone: {phone}
{additional_details}

Please keep this confirmation for your records. If you need to reschedule or cancel, 
please contact us as soon as possible.

Thank you!

Best regards,
Booking Assistant Team
"""

# ============================================
# UI Configuration
# ============================================
PAGE_TITLE = "AI Booking Assistant"
PAGE_ICON = "📅"
LAYOUT = "wide"

# Colors
COLOR_SUCCESS = "#00ff00"
COLOR_ERROR = "#ff0000"
COLOR_WARNING = "#ffaa00"
COLOR_INFO = "#0099ff"

# ============================================
# LLM Configuration
# ============================================
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 1024

GROQ_MODELS = [
    "mixtral-8x7b-32768",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
]

OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-3.5-turbo",
]

GOOGLE_MODELS = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-pro",
]

# ============================================
# RAG Configuration
# ============================================
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_RETRIEVAL_K = 4

# ============================================
# Database Configuration
# ============================================
DEFAULT_DB_PATH = "bookings.db"
SQLALCHEMY_ECHO = False

# ============================================
# Pagination
# ============================================
BOOKINGS_PER_PAGE = 20
MAX_CSV_RECORDS = 10000

# ============================================
# Time Limits
# ============================================
SESSION_TIMEOUT = 3600  # 1 hour in seconds
MEMORY_RETENTION = 1800  # 30 minutes

# ============================================
# Admin Configuration
# ============================================
DEFAULT_ADMIN_PASSWORD = "admin123"
ADMIN_SESSION_TIMEOUT = 1800  # 30 minutes

# ============================================
# Feature Flags
# ============================================
FEATURES = {
    "RAG_ENABLED": True,
    "EMAIL_ENABLED": True,
    "ADMIN_DASHBOARD_ENABLED": True,
    "PDF_UPLOAD_ENABLED": True,
    "BOOKING_CONFIRMATION_ENABLED": True,
}

# ============================================
# Regex Patterns for Extraction
# ============================================
NAME_PATTERN = r'^[a-zA-Z\s\-\'\.]{2,}$'
BOOKING_TYPE_PATTERN = r'(?:' + '|'.join(BOOKING_TYPES) + r')'
