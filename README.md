# AI Booking Assistant

An intelligent, conversational booking assistant powered by LLMs and RAG (Retrieval Augmented Generation). Built with Streamlit, LangChain, and supports multiple LLM providers.

## Features

✨ **Conversational Booking Interface**
- Natural multi-turn dialogue for collecting booking details
- Intelligent slot-filling with contextual awareness
- Automatic entity extraction (name, email, phone, date, time)

📄 **RAG Integration**
- Upload and process PDF documents
- Context-aware responses based on uploaded content
- FAISS vector store for efficient retrieval

💾 **Data Persistence**
- SQLite/Supabase database for booking storage
- Customer and booking relationship management
- Email delivery tracking

📧 **Email Confirmations**
- Automatic booking confirmation emails
- SMTP/SendGrid integration
- Graceful error handling

🎯 **Admin Dashboard**
- View all bookings
- Search and filter by name, date, type, status
- Export bookings as CSV
- Booking statistics and analytics

🚀 **Multi-Provider LLM Support**
- Groq (recommended for speed)
- OpenAI (GPT-4, GPT-3.5)
- Google Gemini

## Project Structure

```
ai-booking-assistant/
├── main.py                  # Streamlit application entry point
├── config.py                # Configuration and environment variables
├── llm.py                   # LLM initialization and provider management
├── chat_logic.py            # Intent detection and conversation management
├── rag_pipeline.py          # PDF processing and RAG implementation
├── tools.py                 # Tool definitions (RAG, Booking, Email)
├── models.py                # SQLAlchemy database models
├── embeddings.py            # Vector store and embeddings setup
├── admin_dashboard.py       # Admin interface
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── .env                     # Environment variables (create this)
```

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-booking-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# LLM Configuration (choose one provider)
# Groq (Recommended)
GROQ_API_KEY=your_groq_api_key
LLM_PROVIDER=groq
LLM_MODEL=mixtral-8x7b-32768

# OR OpenAI
# OPENAI_API_KEY=your_openai_key
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini

# OR Google Gemini
# GOOGLE_API_KEY=your_google_key
# LLM_PROVIDER=google
# LLM_MODEL=gemini-1.5-flash

# Database Configuration
DB_PATH=bookings.db
DATABASE_URL=sqlite:///bookings.db

# Email Configuration (Optional)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Embeddings Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_STORE_PATH=./vector_store

# Admin Configuration
ADMIN_PASSWORD=your_secure_password

# Conversation Configuration
MAX_HISTORY=25
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 3. Get API Keys

#### Groq
1. Visit [Groq Console](https://console.groq.com/keys)
2. Create a new API key
3. Copy and paste in `.env`

#### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy and paste in `.env`

#### Google Gemini
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy and paste in `.env`

#### Gmail (for email confirmations)
1. Enable 2FA on your Google account
2. Create an [App Password](https://myaccount.google.com/apppasswords)
3. Use the generated password in `.env`

## Running the Application

### Development Mode

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`

### Production Deployment

#### Streamlit Cloud

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Select your repository
4. Add secrets in Streamlit Cloud settings

#### Docker

```bash
docker build -t ai-booking-assistant .
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e LLM_PROVIDER=groq \
  ai-booking-assistant
```

## Usage Guide

### For Users

1. **Navigate to Chat** - Select "Chat" from the sidebar
2. **Upload Documents** (Optional) - Add PDF files for context
3. **Make a Booking** - Start with a natural message like:
   - "I want to book a doctor appointment"
   - "Can I reserve a salon slot?"
   - "Book a hotel room for me"

4. **Follow the Flow** - The assistant will ask for:
   - Your name
   - Email address
   - Phone number
   - Service type
   - Preferred date (YYYY-MM-DD)
   - Preferred time (HH:MM)

5. **Confirm** - Review details and confirm
6. **Receive Booking ID** - Your booking is saved and confirmation email sent

### For Admins

1. **Login** - Click "Admin Dashboard" → Enter password (default: admin123)
2. **View Bookings** - See all bookings in a table
3. **Search & Filter** - By name, date, type, or status
4. **Export** - Download bookings as CSV
5. **Statistics** - View booking trends and metrics

## Core Modules

### config.py
Centralized configuration for all environment variables and settings.

### llm.py
Handles LLM provider initialization. Supports:
- Groq ChatGroq
- OpenAI ChatOpenAI
- Google ChatGoogleGenerativeAI

### chat_logic.py
Contains `ChatLogic` class for:
- Intent detection (booking vs general query)
- Entity extraction (email, phone, date, time)
- Conversation memory management
- System prompt generation

`BookingFlowManager` manages booking state machine:
- State transitions
- Slot filling
- Data collection

### rag_pipeline.py
RAGPipeline class for:
- PDF loading and processing
- Text chunking
- Vector store creation/management
- Document retrieval

### tools.py
Three main tools for LLM:
1. **RAGTool** - Retrieve relevant PDF content
2. **BookingPersistenceTool** - Save bookings to database
3. **EmailTool** - Send confirmation emails

### models.py
SQLAlchemy ORM models:
- `Customer` - Customer details (name, email, phone)
- `Booking` - Booking details (date, time, type, status)

### admin_dashboard.py
Streamlit pages for admin interface:
- Login authentication
- Booking table view
- Search and filtering
- Statistics and analytics

## Booking Flow Diagram

```
User Input
    ↓
Intent Detection (Booking vs Query)
    ├→ Booking Intent
    │   ↓
    │  Extract Entities
    │   ↓
    │  Collect Missing Fields
    │   ├→ Name
    │   ├→ Email
    │   ├→ Phone
    │   ├→ Service Type
    │   ├→ Date
    │   └→ Time
    │   ↓
    │  Summarize Details
    │   ↓
    │  Ask Confirmation
    │   ↓
    │  Save to DB
    │   ↓
    │  Send Email
    │   ↓
    │  Return Booking ID
    │
    └→ General Query
        ↓
       Retrieve Context (if RAG enabled)
        ↓
       Generate Response
```

## Error Handling

The application handles:
- ✅ Missing API keys - Shows helpful error messages
- ✅ Invalid PDF files - Graceful error with recovery
- ✅ Database errors - Validation and connection handling
- ✅ Email failures - Booking saved even if email fails
- ✅ Invalid input - Date/email/phone validation
- ✅ Runtime errors - Try-catch with user-friendly messages

## Database Schema

### Customers Table
```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Bookings Table
```sql
CREATE TABLE bookings (
    booking_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    booking_type VARCHAR(100) NOT NULL,
    booking_date VARCHAR(20) NOT NULL,
    booking_time VARCHAR(10) NOT NULL,
    status VARCHAR(50) DEFAULT 'confirmed',
    additional_details VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    email_sent INTEGER DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

## Supported Booking Types

- 👨‍⚕️ Doctor
- 💇 Salon
- 🏨 Hotel
- 🎉 Events
- 📚 Classes
- 🍽️ Restaurant
- 💪 Gym
- 🧖 Spa

(Easily extendable - add to `BOOKING_KEYWORDS` in `chat_logic.py`)

## Troubleshooting

### Issue: "API Key not set"
- Solution: Add API key to `.env` and restart Streamlit

### Issue: PDF not loading
- Solution: Ensure PDF is valid and not password-protected

### Issue: Emails not sending
- Solution: 
  - Enable 2FA on Google account
  - Create App Password
  - Use app password in `.env`
  - Check SMTP settings

### Issue: Database locked
- Solution: Restart Streamlit, close other connections

### Issue: Slow responses
- Solution: Use faster model (Groq recommended), reduce chunk size

## Security Notes

⚠️ **Important for Production:**

1. Change default admin password
2. Use environment variables, never hardcode secrets
3. Use HTTPS in production
4. Validate all user inputs
5. Use secure email (OAuth2 for Gmail)
6. Regular database backups
7. Rate limiting for API calls
8. Add authentication for chat interface (optional)

## Performance Optimization

- Use Groq for fastest inference
- Reduce MAX_HISTORY if memory issues
- Decrease CHUNK_SIZE for faster retrieval
- Use `faiss-gpu` for large vector stores
- Implement caching for frequent queries

## Future Enhancements

- [ ] Booking modifications/cancellations
- [ ] Multi-language support
- [ ] SMS confirmations
- [ ] Calendar integration
- [ ] Payment processing
- [ ] User authentication
- [ ] Analytics dashboard
- [ ] Webhook integrations
- [ ] Voice interaction
- [ ] WhatsApp integration

## License

MIT License - Feel free to use and modify

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in browser console
3. Check Streamlit documentation
4. Verify API keys and configuration

## Contact

Created for AI Engineering Assignment - August 2026
