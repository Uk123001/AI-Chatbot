"""
Utility functions for validation, formatting, and helper operations
"""

import re
from datetime import datetime
from typing import Tuple, Optional
import constants


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not email:
        return False, "Email is required"
    
    pattern = constants.VALIDATION_PATTERNS["email"]
    if re.match(pattern, email):
        return True, "Valid email"
    else:
        return False, constants.ERROR_MESSAGES["INVALID_EMAIL"]


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not phone:
        return False, "Phone is required"
    
    pattern = constants.VALIDATION_PATTERNS["phone"]
    if re.match(pattern, phone):
        return True, "Valid phone"
    else:
        return False, constants.ERROR_MESSAGES["INVALID_PHONE"]


def validate_date(date_str: str) -> Tuple[bool, str]:
    """
    Validate date format (YYYY-MM-DD)
    
    Args:
        date_str: Date string to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not date_str:
        return False, "Date is required"
    
    pattern = constants.VALIDATION_PATTERNS["date"]
    if not re.match(pattern, date_str):
        return False, constants.ERROR_MESSAGES["INVALID_DATE"]
    
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, "Valid date"
    except ValueError:
        return False, "Invalid date"


def validate_time(time_str: str) -> Tuple[bool, str]:
    """
    Validate time format (HH:MM in 24-hour)
    
    Args:
        time_str: Time string to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not time_str:
        return False, "Time is required"
    
    pattern = constants.VALIDATION_PATTERNS["time"]
    if re.match(pattern, time_str):
        return True, "Valid time"
    else:
        return False, constants.ERROR_MESSAGES["INVALID_TIME"]


def validate_name(name: str) -> Tuple[bool, str]:
    """
    Validate name format
    
    Args:
        name: Name to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not name:
        return False, "Name is required"
    
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 100:
        return False, "Name must be less than 100 characters"
    
    # Allow letters, spaces, hyphens, apostrophes, periods
    pattern = r'^[a-zA-Z\s\-\'\.]{2,}$'
    if re.match(pattern, name):
        return True, "Valid name"
    else:
        return False, "Name contains invalid characters"


def validate_booking_type(booking_type: str) -> Tuple[bool, str]:
    """
    Validate booking type
    
    Args:
        booking_type: Booking type to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not booking_type:
        return False, "Booking type is required"
    
    booking_type_lower = booking_type.lower().strip()
    
    if booking_type_lower in constants.BOOKING_TYPES:
        return True, "Valid booking type"
    else:
        valid_types = ", ".join(constants.BOOKING_TYPES)
        return False, f"Invalid booking type. Valid types: {valid_types}"


def format_booking_summary(booking_data: dict) -> str:
    """
    Format booking data for display
    
    Args:
        booking_data: Booking data dictionary
    
    Returns:
        Formatted booking summary string
    """
    emoji = constants.BOOKING_TYPE_EMOJIS.get(booking_data.get("booking_type"), "📅")
    
    summary = f"""
{emoji} **Booking Summary**

**Customer Information:**
- Name: {booking_data.get('name', 'N/A')}
- Email: {booking_data.get('email', 'N/A')}
- Phone: {booking_data.get('phone', 'N/A')}

**Booking Details:**
- Service Type: {booking_data.get('booking_type', 'N/A')}
- Date: {booking_data.get('date', 'N/A')}
- Time: {booking_data.get('time', 'N/A')}
- Additional Details: {booking_data.get('details', 'None')}
"""
    return summary


def format_confirmation_email(booking_data: dict, booking_id: int) -> Tuple[str, str]:
    """
    Format confirmation email subject and body
    
    Args:
        booking_data: Booking data dictionary
        booking_id: Generated booking ID
    
    Returns:
        Tuple of (subject, body)
    """
    subject = constants.EMAIL_SUBJECT_TEMPLATE.format(booking_id=booking_id)
    
    additional_details = ""
    if booking_data.get("details"):
        additional_details = f"Additional Details: {booking_data.get('details')}"
    
    body = constants.EMAIL_BODY_TEMPLATE.format(
        name=booking_data.get('name', 'Valued Customer'),
        booking_id=booking_id,
        booking_type=booking_data.get('booking_type', 'Service'),
        date=booking_data.get('date', 'N/A'),
        time=booking_data.get('time', 'N/A'),
        email=booking_data.get('email', 'N/A'),
        phone=booking_data.get('phone', 'N/A'),
        additional_details=additional_details
    )
    
    return subject, body


def extract_entities_from_message(message: str) -> dict:
    """
    Extract common entities from a message
    
    Args:
        message: Input message
    
    Returns:
        Dictionary of extracted entities
    """
    entities = {
        "email": None,
        "phone": None,
        "date": None,
        "time": None,
        "booking_type": None
    }
    
    # Email extraction
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, message)
    if email_match:
        entities["email"] = email_match.group()
    
    # Phone extraction
    phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
    phone_match = re.search(phone_pattern, message)
    if phone_match:
        entities["phone"] = phone_match.group()
    
    # Date extraction
    date_pattern = r'\b(\d{4})-(\d{2})-(\d{2})\b'
    date_match = re.search(date_pattern, message)
    if date_match:
        entities["date"] = date_match.group()
    
    # Time extraction
    time_pattern = r'\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b'
    time_match = re.search(time_pattern, message)
    if time_match:
        entities["time"] = time_match.group()
    
    # Booking type extraction
    for booking_type in constants.BOOKING_TYPES:
        if booking_type in message.lower():
            entities["booking_type"] = booking_type
            break
    
    return entities


def is_confirmation_message(message: str) -> bool:
    """
    Check if message is a confirmation (yes/no)
    
    Args:
        message: Input message
    
    Returns:
        True if message indicates confirmation
    """
    confirmation_keywords = ["yes", "confirm", "proceed", "go ahead", "y", "yep", "sure", "ok", "okay"]
    message_lower = message.lower().strip()
    return message_lower in confirmation_keywords


def is_cancellation_message(message: str) -> bool:
    """
    Check if message is a cancellation (no/cancel)
    
    Args:
        message: Input message
    
    Returns:
        True if message indicates cancellation
    """
    cancellation_keywords = ["no", "cancel", "stop", "abort", "n", "nope", "dont", "don't"]
    message_lower = message.lower().strip()
    return message_lower in cancellation_keywords


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def get_emoji_for_booking_type(booking_type: str) -> str:
    """
    Get emoji for a booking type
    
    Args:
        booking_type: Booking type
    
    Returns:
        Emoji string
    """
    return constants.BOOKING_TYPE_EMOJIS.get(booking_type.lower(), "📅")


def format_date_display(date_str: str) -> str:
    """
    Format date for display (YYYY-MM-DD to human readable)
    
    Args:
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str


def format_time_display(time_str: str) -> str:
    """
    Format time for display (24-hour to 12-hour)
    
    Args:
        time_str: Time in HH:MM format
    
    Returns:
        Formatted time string
    """
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%I:%M %p")
    except:
        return time_str


def get_next_available_date() -> str:
    """
    Get next available booking date (tomorrow)
    
    Returns:
        Date in YYYY-MM-DD format
    """
    from datetime import timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")


def is_valid_booking_data(booking_data: dict) -> Tuple[bool, str]:
    """
    Validate complete booking data
    
    Args:
        booking_data: Dictionary with booking information
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["name", "email", "phone", "booking_type", "date", "time"]
    
    # Check all required fields present
    missing_fields = [field for field in required_fields if not booking_data.get(field)]
    if missing_fields:
        return False, f"Missing fields: {', '.join(missing_fields)}"
    
    # Validate each field
    name_valid, name_msg = validate_name(booking_data["name"])
    if not name_valid:
        return False, name_msg
    
    email_valid, email_msg = validate_email(booking_data["email"])
    if not email_valid:
        return False, email_msg
    
    phone_valid, phone_msg = validate_phone(booking_data["phone"])
    if not phone_valid:
        return False, phone_msg
    
    type_valid, type_msg = validate_booking_type(booking_data["booking_type"])
    if not type_valid:
        return False, type_msg
    
    date_valid, date_msg = validate_date(booking_data["date"])
    if not date_valid:
        return False, date_msg
    
    time_valid, time_msg = validate_time(booking_data["time"])
    if not time_valid:
        return False, time_msg
    
    return True, "All fields valid"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
