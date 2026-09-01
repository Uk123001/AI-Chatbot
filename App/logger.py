"""
Logging configuration for AI Booking Assistant
"""

import logging
import os
from datetime import datetime

# Create logs directory
os.makedirs("logs", exist_ok=True)

# Log file path
log_file = f"logs/booking_assistant_{datetime.now().strftime('%Y%m%d')}.log"

# Create logger
logger = logging.getLogger("ai_booking_assistant")
logger.setLevel(logging.DEBUG)

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

simple_formatter = logging.Formatter(
    '%(levelname)s - %(message)s'
)

# File handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(simple_formatter)
logger.addHandler(console_handler)


# Module-specific loggers
def get_module_logger(module_name: str) -> logging.Logger:
    """Get logger for a specific module"""
    return logging.getLogger(f"ai_booking_assistant.{module_name}")


# Loggers for different modules
chat_logger = get_module_logger("chat")
rag_logger = get_module_logger("rag")
db_logger = get_module_logger("database")
email_logger = get_module_logger("email")
admin_logger = get_module_logger("admin")
llm_logger = get_module_logger("llm")
