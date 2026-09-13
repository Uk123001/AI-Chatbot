import re
from typing import Tuple, Dict, List


class ChatLogic:
    """Handles chat logic, intent detection, and memory"""
    
    # Intent detection patterns
    BOOKING_KEYWORDS = [
        "book", "appointment", "reservation", "schedule", "booking",
        "doctor", "salon", "hotel", "event", "class", "classes",
        "reserve", "I want to", "I'd like to", "can I", "could I"
    ]
    
    CONFIRMATION_KEYWORDS = ["yes", "confirm", "proceed", "go ahead", "y", "yep", "sure"]
    
    def __init__(self):
        self.memory = []
        self.max_memory = 25
    
    def detect_intent(self, message: str) -> str:
        """Detect if message is booking-related or general query"""
        message_lower = message.lower()
        
        # Check for booking intent
        if any(keyword in message_lower for keyword in self.BOOKING_KEYWORDS):
            return "booking"
        
        # Check for confirmation
        if any(keyword in message_lower for keyword in self.CONFIRMATION_KEYWORDS):
            return "confirmation"
        
        # Default to general query
        return "general"
    
    def extract_entities(self, message: str) -> Dict:
        """Extract relevant entities from message"""
        entities = {
            "name": None,
            "email": None,
            "phone": None,
            "date": None,
            "time": None,
            "booking_type": None,
            "details": None
        }
        
        # Email pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, message)
        if email_match:
            entities["email"] = email_match.group()
        
        # Phone pattern (basic)
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            entities["phone"] = phone_match.group()
        
        # Date pattern (YYYY-MM-DD or DD-MM-YYYY or DD/MM/YYYY)
        date_pattern = r'\b(?:(\d{4})-(\d{2})-(\d{2})|(\d{1,2})[/-](\d{1,2})[/-](\d{4}))\b'
        date_match = re.search(date_pattern, message)
        if date_match:
            if date_match.group(1):  # YYYY-MM-DD format
                entities["date"] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            else:  # DD/MM/YYYY format
                entities["date"] = f"{date_match.group(6)}-{date_match.group(5)}-{date_match.group(4)}"
        
        # Time pattern (HH:MM)
        time_pattern = r'\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b'
        time_match = re.search(time_pattern, message)
        if time_match:
            entities["time"] = time_match.group()
        
        # Booking type detection
        booking_types = ["doctor", "salon", "hotel", "events", "classes", "restaurant", "gym", "spa"]
        for booking_type in booking_types:
            if booking_type in message.lower():
                entities["booking_type"] = booking_type
                break
        
        return entities
    
    def add_to_memory(self, role: str, content: str):
        """Add message to conversation memory"""
        self.memory.append({
            "role": role,
            "content": content
        })
        
        # Keep only last N messages
        if len(self.memory) > self.max_memory:
            self.memory = self.memory[-self.max_memory:]
    
    def get_memory(self) -> List[Dict]:
        """Get conversation memory"""
        return self.memory
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory = []
    
    def get_system_prompt(self) -> str:
        """Get system prompt for the chatbot"""
        return """You are an AI Booking Assistant. Your primary role is to help customers make bookings for various services.

Key responsibilities:
1. Detect if the user wants to make a booking or is asking a general question
2. For booking requests:
   - Collect required information: name, email, phone, booking type, date, and time
   - Ask for missing information one at a time
   - Only collect information that hasn't been provided yet
   - Summarize the booking details before confirmation
   - Ask for explicit confirmation before saving

3. For general queries:
   - Answer questions based on uploaded PDF documents when available
   - Be helpful and concise

Important guidelines:
- Be friendly and professional
- Don't repeat information already provided
- Validate email and phone format
- Ensure date is in valid format (YYYY-MM-DD)
- Ensure time is in valid format (HH:MM)
- Always ask for confirmation before saving booking
- After confirmation, provide the booking ID

When collecting booking information, follow this flow:
1. Detect booking intent
2. Extract known details from the message
3. Ask for missing required fields one at a time
4. Maintain conversation context using memory
5. Summarize details
6. Ask for confirmation
7. Save and provide booking ID"""


class BookingFlowManager:
    """Manages the booking flow state machine"""
    
    BOOKING_STATES = {
        "start": "booking_detected",
        "booking_detected": "collect_name",
        "collect_name": "collect_email",
        "collect_email": "collect_phone",
        "collect_phone": "collect_type",
        "collect_type": "collect_date",
        "collect_date": "collect_time",
        "collect_time": "confirm",
        "confirm": "completed"
    }
    
    def __init__(self):
        self.current_state = "start"
        self.booking_data = {}
    
    def set_state(self, state: str):
        """Set current state"""
        self.current_state = state
    
    def get_state(self) -> str:
        """Get current state"""
        return self.current_state
    
    def get_next_question(self) -> str:
        """Get the next question based on current state"""
        questions = {
            "collect_name": "What is your name?",
            "collect_email": "What is your email address?",
            "collect_phone": "What is your phone number?",
            "collect_type": "What type of booking are you looking for? (e.g., doctor, salon, hotel, events, classes)",
            "collect_date": "What date would you prefer? (Please use YYYY-MM-DD format)",
            "collect_time": "What time would you prefer? (Please use HH:MM format in 24-hour)",
            "confirm": "Please confirm your booking details. Say 'yes' to confirm or 'no' to make changes."
        }
        return questions.get(self.current_state, "")
    
    def update_booking_data(self, key: str, value: str):
        """Update booking data"""
        self.booking_data[key] = value
    
    def get_booking_data(self) -> Dict:
        """Get booking data"""
        return self.booking_data
    
    def reset(self):
        """Reset booking flow"""
        self.current_state = "start"
        self.booking_data = {}
