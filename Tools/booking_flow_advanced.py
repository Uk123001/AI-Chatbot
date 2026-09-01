"""
Advanced booking flow manager with state machine implementation
"""

from enum import Enum
from typing import Optional, Dict, Tuple
from datetime import datetime
import utils
from logger import get_module_logger

logger = get_module_logger("booking_flow")


class BookingState(Enum):
    """Booking flow states"""
    START = "start"
    COLLECT_NAME = "collect_name"
    COLLECT_EMAIL = "collect_email"
    COLLECT_PHONE = "collect_phone"
    COLLECT_TYPE = "collect_type"
    COLLECT_DATE = "collect_date"
    COLLECT_TIME = "collect_time"
    COLLECT_DETAILS = "collect_details"
    SUMMARIZE = "summarize"
    CONFIRM = "confirm"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AdvancedBookingFlowManager:
    """Advanced booking flow manager with validation and state tracking"""
    
    STATE_SEQUENCE = [
        BookingState.COLLECT_NAME,
        BookingState.COLLECT_EMAIL,
        BookingState.COLLECT_PHONE,
        BookingState.COLLECT_TYPE,
        BookingState.COLLECT_DATE,
        BookingState.COLLECT_TIME,
        BookingState.SUMMARIZE,
        BookingState.CONFIRM,
    ]
    
    def __init__(self):
        self.current_state = BookingState.START
        self.booking_data = {}
        self.validated_fields = set()
        self.field_attempts = {}  # Track attempts for error handling
        self.max_attempts = 3
    
    def get_current_state(self) -> BookingState:
        """Get current state"""
        return self.current_state
    
    def set_state(self, state: BookingState):
        """Set state"""
        logger.info(f"State transition: {self.current_state.value} -> {state.value}")
        self.current_state = state
    
    def process_input(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Process user input based on current state
        
        Args:
            user_input: User's input message
        
        Returns:
            Tuple of (success, message, booking_data_if_complete)
        """
        # Check for cancellation
        if utils.is_cancellation_message(user_input):
            self.current_state = BookingState.CANCELLED
            return False, "Booking cancelled. Start a new conversation anytime!", None
        
        # Route based on current state
        if self.current_state == BookingState.START:
            return self._handle_start(user_input)
        elif self.current_state == BookingState.COLLECT_NAME:
            return self._handle_name(user_input)
        elif self.current_state == BookingState.COLLECT_EMAIL:
            return self._handle_email(user_input)
        elif self.current_state == BookingState.COLLECT_PHONE:
            return self._handle_phone(user_input)
        elif self.current_state == BookingState.COLLECT_TYPE:
            return self._handle_type(user_input)
        elif self.current_state == BookingState.COLLECT_DATE:
            return self._handle_date(user_input)
        elif self.current_state == BookingState.COLLECT_TIME:
            return self._handle_time(user_input)
        elif self.current_state == BookingState.SUMMARIZE:
            return self._handle_summarize(user_input)
        elif self.current_state == BookingState.CONFIRM:
            return self._handle_confirm(user_input)
        
        return False, "Invalid state", None
    
    def _handle_start(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle start state - extract initial entities"""
        # Extract entities from user input
        entities = utils.extract_entities_from_message(user_input)
        
        # Store extracted data
        for key, value in entities.items():
            if value:
                self.booking_data[key] = value
                self.validated_fields.add(key)
        
        # Move to next unfilled field
        self._advance_to_next_field()
        
        question = self._get_question_for_state()
        return True, question, None
    
    def _handle_name(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle name collection"""
        is_valid, message = utils.validate_name(user_input)
        
        if not is_valid:
            attempt_key = "name"
            self.field_attempts[attempt_key] = self.field_attempts.get(attempt_key, 0) + 1
            
            if self.field_attempts[attempt_key] >= self.max_attempts:
                logger.warning(f"Max attempts exceeded for name field")
                return False, f"{message} - Please provide a valid name (max 3 attempts).", None
            
            return False, message, None
        
        self.booking_data["name"] = user_input.strip()
        self.validated_fields.add("name")
        self._advance_to_next_field()
        
        question = self._get_question_for_state()
        return True, question, None
    
    def _handle_email(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle email collection"""
        is_valid, message = utils.validate_email(user_input)
        
        if not is_valid:
            attempt_key = "email"
            self.field_attempts[attempt_key] = self.field_attempts.get(attempt_key, 0) + 1
            
            if self.field_attempts[attempt_key] >= self.max_attempts:
                return False, f"{message} - Max attempts exceeded. {utils.ERROR_MESSAGES['MISSING_FIELD']}", None
            
            return False, message, None
        
        self.booking_data["email"] = user_input.strip().lower()
        self.validated_fields.add("email")
        self._advance_to_next_field()
        
        question = self._get_question_for_state()
        return True, question, None
    
    def _handle_phone(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle phone collection"""
        is_valid, message = utils.validate_phone(user_input)
        
        if not is_valid:
            attempt_key = "phone"
            self.field_attempts[attempt_key] = self.field_attempts.get(attempt_key, 0) + 1
            
            if self.field_attempts[attempt_key] >= self.max_attempts:
                return False, f"{message} - Max attempts exceeded. {utils.ERROR_MESSAGES['MISSING_FIELD']}", None
            
            return False, message, None
        
        self.booking_data["phone"] = user_input.strip()
        self.validated_fields.add("phone")
        self._advance_to_next_field()
        
        question = self._get_question_for_state()
        return True, question, None
    
    def _handle_type(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle booking type collection"""
        is_valid, message = utils.validate_booking_type(user_input)
        
        if not is_valid:
            attempt_key = "booking_type"
            self.field_attempts[attempt_key] = self.field_attempts.get(attempt_key, 0) + 1
            
            if self.field_attempts[attempt_key] >= self.max_attempts:
                return False, f"{message} - Max attempts exceeded.", None
            
            return False, message, None
        
        self.booking_data["booking_type"] = user_input.strip().lower()
        self.validated_fields.add("booking_type")
        self._advance_to_next_field()
        
        question = self._get_question_for_state()
        return True, question, None
    
    def _handle_date(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle date collection"""
        is_valid, message = utils.validate_date(user_input)
        
        if not is_valid:
            attempt_key = "date"
            self.field_attempts[attempt_key] = self.field_attempts.get(attempt_key, 0) + 1
            
            if self.field_attempts[attempt_key] >= self.max_attempts:
                return False, f"{message} - Max attempts exceeded.", None
            
            return False, message, None
        
        self.booking_data["date"] = user_input.strip()
        self.validated_fields.add("date")
        self._advance_to_next_field()
        
        question = self._get_question_for_state()
        return True, question, None
    
    def _handle_time(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle time collection"""
        is_valid, message = utils.validate_time(user_input)
        
        if not is_valid:
            attempt_key = "time"
            self.field_attempts[attempt_key] = self.field_attempts.get(attempt_key, 0) + 1
            
            if self.field_attempts[attempt_key] >= self.max_attempts:
                return False, f"{message} - Max attempts exceeded.", None
            
            return False, message, None
        
        self.booking_data["time"] = user_input.strip()
        self.validated_fields.add("time")
        self._advance_to_next_field()
        
        question = self._get_question_for_state()
        return True, question, None
    
    def _handle_summarize(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle summarize state"""
        self.set_state(BookingState.CONFIRM)
        summary = utils.format_booking_summary(self.booking_data)
        
        confirm_question = "Is this information correct? (yes/no)"
        return True, f"{summary}\n{confirm_question}", None
    
    def _handle_confirm(self, user_input: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle confirmation"""
        if utils.is_confirmation_message(user_input):
            self.set_state(BookingState.COMPLETED)
            logger.info(f"Booking confirmed: {self.booking_data}")
            return True, "Booking confirmed! Processing...", self.booking_data
        elif utils.is_cancellation_message(user_input):
            self.set_state(BookingState.CANCELLED)
            return False, "Booking cancelled. Let's start over.", None
        else:
            return False, "Please answer yes or no to confirm your booking.", None
    
    def _advance_to_next_field(self):
        """Advance to next unfilled field"""
        # Define field order
        field_order = ["name", "email", "phone", "booking_type", "date", "time"]
        
        for field in field_order:
            if field not in self.validated_fields:
                # Map field to state
                field_to_state = {
                    "name": BookingState.COLLECT_NAME,
                    "email": BookingState.COLLECT_EMAIL,
                    "phone": BookingState.COLLECT_PHONE,
                    "booking_type": BookingState.COLLECT_TYPE,
                    "date": BookingState.COLLECT_DATE,
                    "time": BookingState.COLLECT_TIME,
                }
                self.set_state(field_to_state.get(field, BookingState.SUMMARIZE))
                return
        
        # All required fields filled
        self.set_state(BookingState.SUMMARIZE)
    
    def _get_question_for_state(self) -> str:
        """Get question for current state"""
        state_questions = {
            BookingState.COLLECT_NAME: "What is your name?",
            BookingState.COLLECT_EMAIL: "What is your email address?",
            BookingState.COLLECT_PHONE: "What is your phone number?",
            BookingState.COLLECT_TYPE: "What type of booking are you looking for? (e.g., doctor, salon, hotel)",
            BookingState.COLLECT_DATE: "What date do you prefer? (YYYY-MM-DD format)",
            BookingState.COLLECT_TIME: "What time do you prefer? (HH:MM format, 24-hour)",
        }
        
        return state_questions.get(self.current_state, "")
    
    def get_booking_data(self) -> Dict:
        """Get current booking data"""
        return self.booking_data
    
    def reset(self):
        """Reset booking flow"""
        self.current_state = BookingState.START
        self.booking_data = {}
        self.validated_fields = set()
        self.field_attempts = {}
        logger.info("Booking flow reset")
    
    def get_progress(self) -> Tuple[int, int]:
        """Get progress percentage"""
        total_fields = 6  # name, email, phone, type, date, time
        filled = len(self.validated_fields)
        return filled, total_fields
