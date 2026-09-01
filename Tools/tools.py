import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import config
from models import get_session, Customer, Booking


class RAGTool:
    """Tool for RAG retrieval"""
    
    @staticmethod
    def execute(query: str, rag_pipeline) -> str:
        """Execute RAG query"""
        result = rag_pipeline.rag_query(query)
        
        if result["has_context"]:
            return result["context"]
        else:
            return "No relevant information found in uploaded documents."


class BookingPersistenceTool:
    """Tool for storing bookings in database"""
    
    @staticmethod
    def execute(booking_data: dict) -> dict:
        """Save booking to database"""
        try:
            session = get_session()
            
            # Check if customer exists
            customer = session.query(Customer).filter_by(email=booking_data["email"]).first()
            
            if not customer:
                # Create new customer
                customer = Customer(
                    name=booking_data["name"],
                    email=booking_data["email"],
                    phone=booking_data["phone"]
                )
                session.add(customer)
                session.flush()  # Get customer_id
            
            # Create booking
            booking = Booking(
                customer_id=customer.customer_id,
                booking_type=booking_data["booking_type"],
                booking_date=booking_data["date"],
                booking_time=booking_data["time"],
                status="confirmed",
                additional_details=booking_data.get("details", "")
            )
            session.add(booking)
            session.commit()
            
            booking_id = booking.booking_id
            session.close()
            
            return {
                "success": True,
                "booking_id": booking_id,
                "message": f"Booking #{booking_id} saved successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "booking_id": None,
                "message": f"Error saving booking: {str(e)}"
            }


class EmailTool:
    """Tool for sending confirmation emails"""
    
    @staticmethod
    def execute(email_data: dict) -> dict:
        """Send confirmation email"""
        try:
            # Check if email credentials are configured
            if not config.SENDER_EMAIL or not config.SENDER_PASSWORD:
                return {
                    "success": False,
                    "message": "Email service not configured. Booking saved but email not sent."
                }
            
            # Create email content
            subject = f"Booking Confirmation - #{email_data['booking_id']}"
            
            body = f"""
Dear {email_data['name']},

Thank you for your booking! Here are your confirmation details:

Booking ID: {email_data['booking_id']}
Date: {email_data['date']}
Time: {email_data['time']}
Service Type: {email_data['booking_type']}
Name: {email_data['name']}
Email: {email_data['email']}
Phone: {email_data['phone']}
{f"Additional Details: {email_data['details']}" if email_data.get('details') else ""}

Please keep this confirmation for your records. If you need to reschedule or cancel, 
please contact us as soon as possible.

Thank you!

Best regards,
Booking Assistant Team
            """
            
            # Send email
            message = MIMEMultipart()
            message["From"] = config.SENDER_EMAIL
            message["To"] = email_data["email"]
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            
            server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
            server.starttls()
            server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
            server.send_message(message)
            server.quit()
            
            # Update email_sent flag in database
            try:
                session = get_session()
                booking = session.query(Booking).filter_by(booking_id=email_data['booking_id']).first()
                if booking:
                    booking.email_sent = 1
                    session.commit()
                session.close()
            except:
                pass
            
            return {
                "success": True,
                "message": f"Confirmation email sent to {email_data['email']}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending email: {str(e)}"
            }


def get_tools():
    """Get available tools for the LLM"""
    tools = [
        {
            "name": "rag_tool",
            "description": "Search uploaded PDF documents for booking-related information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "booking_persistence_tool",
            "description": "Save booking details to the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer name"},
                    "email": {"type": "string", "description": "Customer email"},
                    "phone": {"type": "string", "description": "Customer phone"},
                    "booking_type": {"type": "string", "description": "Type of booking (doctor/salon/hotel/events/classes)"},
                    "date": {"type": "string", "description": "Booking date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Booking time in HH:MM format"},
                    "details": {"type": "string", "description": "Additional details"}
                },
                "required": ["name", "email", "phone", "booking_type", "date", "time"]
            }
        },
        {
            "name": "email_tool",
            "description": "Send confirmation email to customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer name"},
                    "email": {"type": "string", "description": "Customer email"},
                    "phone": {"type": "string", "description": "Customer phone"},
                    "booking_id": {"type": "integer", "description": "Booking ID"},
                    "date": {"type": "string", "description": "Booking date"},
                    "time": {"type": "string", "description": "Booking time"},
                    "booking_type": {"type": "string", "description": "Type of booking"},
                    "details": {"type": "string", "description": "Additional details"}
                },
                "required": ["name", "email", "booking_id", "date", "time", "booking_type"]
            }
        }
    ]
    return tools
