# AI Booking Assistant - Project Files Overview

## Complete File Structure

```
ai-booking-assistant/
├── 📄 CORE APPLICATION
│   ├── main.py                           # Entry point - Streamlit app
│   ├── config.py                         # Configuration management
│   ├── constants.py                      # Application constants & enums
│   ├── logger.py                         # Logging configuration
│   └── utils.py                          # Utility functions
│
├── 🤖 LLM & AI
│   ├── llm.py                           # LLM provider initialization
│   ├── chat_logic.py                    # Intent detection & conversation flow
│   └── rag_pipeline.py                  # PDF processing & RAG
│
├── 💾 DATABASE & MODELS
│   ├── models.py                        # SQLAlchemy ORM models
│   └── embeddings.py                    # Vector store setup
│
├── 🛠️ TOOLS & FEATURES
│   ├── tools.py                         # RAG, Booking, Email tools
│   └── booking_flow_advanced.py         # Advanced booking state machine
│
├── 📊 ADMIN INTERFACE
│   └── admin_dashboard.py               # Admin dashboard & management
│
├── 🐳 DEPLOYMENT
│   ├── Dockerfile                       # Docker image configuration
│   ├── docker-compose.yml               # Docker Compose setup
│   └── .streamlit_config.toml           # Streamlit configuration
│
├── 📖 DOCUMENTATION
│   ├── README.md                        # Complete documentation
│   ├── QUICKSTART.md                    # Quick start guide
│   ├── DEPLOYMENT.md                    # Production deployment guide
│   └── FILE_STRUCTURE.md                # This file
│
├── ⚙️ CONFIGURATION
│   ├── requirements.txt                 # Python dependencies
│   ├── .env.example                     # Environment variables template
│   ├── .gitignore                       # Git ignore rules
│   └── .env                             # (Create this) Actual env variables
│
└── 📁 RUNTIME (Created when running)
    ├── bookings.db                      # SQLite database
    ├── vector_store/                    # FAISS vector store
    └── logs/                            # Application logs
```

## File Descriptions

### Core Application Files

#### main.py
- **Purpose**: Streamlit application entry point
- **Key Functions**:
  - `initialize_session_state()` - Set up session variables
  - `chat_page()` - Main chat interface
  - `instructions_page()` - Setup instructions
  - `main()` - Application router
- **Key Features**:
  - Streamlit navigation (Chat, Instructions, Admin Dashboard)
  - PDF upload and RAG integration
  - Chat message display and input
  - Session state management

#### config.py
- **Purpose**: Centralized configuration management
- **Includes**:
  - API keys (Groq, OpenAI, Google)
  - Database configuration
  - Email settings
  - Vector store paths
  - Conversation limits
  - Page configuration
- **Usage**: Import and use for any configuration values

#### constants.py
- **Purpose**: Application-wide constants and enums
- **Contains**:
  - Booking types and status enums
  - Chat intent types
  - Booking flow states
  - Validation patterns (regex)
  - Error/success messages
  - LLM model lists
  - UI colors and configuration

#### logger.py
- **Purpose**: Structured logging configuration
- **Features**:
  - File and console handlers
  - Multiple log levels
  - Module-specific loggers
  - Automatic log rotation
- **Usage**: `from logger import get_module_logger; logger = get_module_logger("chat")`

#### utils.py
- **Purpose**: Reusable utility functions
- **Functions**:
  - Validation: `validate_email()`, `validate_phone()`, `validate_date()`, etc.
  - Formatting: `format_booking_summary()`, `format_confirmation_email()`
  - Entity extraction: `extract_entities_from_message()`
  - Text processing: `clean_text()`, `truncate_text()`
  - Display formatting: `format_date_display()`, `format_time_display()`

### LLM & AI Files

#### llm.py
- **Purpose**: LLM provider management
- **Providers**:
  - Groq (ChatGroq)
  - OpenAI (ChatOpenAI)
  - Google (ChatGoogleGenerativeAI)
- **Key Functions**:
  - `get_chat_model()` - Get model based on config
  - `get_groq_model()` - Initialize Groq
  - `get_openai_model()` - Initialize OpenAI
  - `get_google_model()` - Initialize Google

#### chat_logic.py
- **Purpose**: Conversation logic and flow management
- **Classes**:
  - `ChatLogic`: Intent detection, entity extraction, memory
  - `BookingFlowManager`: Booking state machine
- **Key Features**:
  - Intent detection (booking vs general)
  - Entity extraction with regex
  - Conversation memory management
  - System prompt generation

#### rag_pipeline.py
- **Purpose**: RAG (Retrieval Augmented Generation)
- **Class**: `RAGPipeline`
- **Features**:
  - PDF ingestion and loading
  - Text chunking and splitting
  - Vector store creation/loading
  - Document retrieval
  - Query handling

### Database & Models

#### models.py
- **Purpose**: SQLAlchemy ORM models
- **Models**:
  - `Customer`: customer_id, name, email, phone, created_at
  - `Booking`: booking_id, customer_id, booking_type, date, time, status, etc.
- **Functions**:
  - `init_db()` - Initialize database
  - `get_session()` - Get database session

#### embeddings.py
- **Purpose**: Vector store and embeddings
- **Functions**:
  - `get_embeddings_model()` - Get embeddings model
  - `create_vector_store()` - Create FAISS store
  - `load_vector_store()` - Load existing store
  - `retrieve_documents()` - Retrieve from store

### Tools & Features

#### tools.py
- **Purpose**: Tool implementations for LLM
- **Classes**:
  - `RAGTool`: PDF retrieval
  - `BookingPersistenceTool`: Database saving
  - `EmailTool`: Email sending
- **Functions**:
  - `get_tools()` - Get tool definitions

#### booking_flow_advanced.py
- **Purpose**: Advanced booking flow with state machine
- **Classes**:
  - `BookingState`: Enum of states
  - `AdvancedBookingFlowManager`: Sophisticated flow management
- **Features**:
  - State machine implementation
  - Field validation with retry logic
  - Progress tracking
  - Error handling

### Admin Interface

#### admin_dashboard.py
- **Purpose**: Admin management interface
- **Functions**:
  - `admin_dashboard()` - Main dashboard
  - `show_admin_login()` - Login page
  - `show_all_bookings()` - Display all bookings
  - `show_search_filter()` - Search interface
  - `show_statistics()` - Analytics

### Configuration Files

#### requirements.txt
- **Purpose**: Python package dependencies
- **Includes**:
  - Framework: Streamlit
  - LLM: LangChain, Groq, OpenAI, Google
  - PDF: PyPDF2
  - Embeddings: Sentence Transformers, FAISS
  - Database: SQLAlchemy
  - Others: Pandas, NumPy, Requests

#### .env.example
- **Purpose**: Template for environment variables
- **Sections**:
  - LLM provider config
  - Database settings
  - Email configuration
  - Embeddings settings
  - Admin settings

#### Dockerfile
- **Purpose**: Docker image configuration
- **Stages**:
  - Base: Python 3.10 slim
  - Builder: Install dependencies
  - Runtime: Final image
- **Exposes**: Port 8501

#### docker-compose.yml
- **Purpose**: Docker Compose orchestration
- **Services**:
  - app: Streamlit application
  - postgres: (Optional) PostgreSQL database
- **Features**:
  - Volume mounts
  - Health checks
  - Environment variables

### Documentation Files

#### README.md
- **Sections**:
  - Features and capabilities
  - Installation instructions
  - Configuration guide
  - Usage instructions
  - Core module descriptions
  - Booking flow diagram
  - Database schema
  - Troubleshooting
  - Security notes
  - Future enhancements

#### QUICKSTART.md
- **Content**:
  - 5-minute setup guide
  - API key acquisition
  - Installation steps
  - Configuration
  - Running the app
  - Common issues
  - Next steps

#### DEPLOYMENT.md
- **Sections**:
  - Local development
  - Docker deployment
  - Streamlit Cloud
  - Production server setup
  - Database options
  - Security checklist
  - Performance optimization
  - Monitoring setup
  - Scaling strategy

## How Files Work Together

### Application Flow
```
User Input (Streamlit UI)
    ↓
main.py (Route to appropriate page)
    ├→ chat_page()
    │   ├→ chat_logic.py (Intent detection)
    │   ├→ rag_pipeline.py (Retrieve context)
    │   ├→ llm.py (Get model response)
    │   └→ tools.py (Execute actions)
    │       ├→ RAGTool
    │       ├→ BookingPersistenceTool
    │       │   └→ models.py (Save to DB)
    │       └→ EmailTool
    │
    ├→ instructions_page()
    │   └→ Display help
    │
    └→ admin_dashboard()
        └→ admin_dashboard.py (View bookings)
```

### Database Flow
```
Booking Data
    ↓
tools.py (BookingPersistenceTool)
    ↓
models.py (ORM)
    ↓
SQLite / PostgreSQL
```

### RAG Flow
```
PDF Upload
    ↓
rag_pipeline.py (Process)
    ├→ PDF Loading
    ├→ Text Chunking
    └→ Vector Store
        ↓
Query
    ↓
Retrieval & Ranking
    ↓
Context to LLM
```

## File Dependencies

### main.py depends on:
- config.py, constants.py, logger.py, utils.py
- llm.py, chat_logic.py, rag_pipeline.py
- admin_dashboard.py, tools.py, models.py

### chat_logic.py depends on:
- constants.py, utils.py, logger.py

### rag_pipeline.py depends on:
- config.py, embeddings.py, logger.py

### admin_dashboard.py depends on:
- models.py, constants.py, logger.py

### tools.py depends on:
- models.py, config.py, logger.py, rag_pipeline.py

## Configuration Priority

1. Environment Variables (.env file)
2. config.py defaults
3. constants.py fallbacks

## Database Initialization

The application automatically creates tables on first run:
- `customers` table
- `bookings` table

No manual SQL required!

## Vector Store Location

- **Default**: `./vector_store/`
- **Configurable**: Set `VECTOR_STORE_PATH` in .env
- **Files**: FAISS index files (automatically created)

## Logging Locations

- **Console**: stdout (configurable level)
- **Files**: `logs/booking_assistant_YYYYMMDD.log`
- **Format**: Timestamp, Logger, Level, Function, Line, Message

## Environment Variables Used

See config.py for complete list. Key variables:
- `GROQ_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`
- `LLM_PROVIDER`, `LLM_MODEL`
- `DATABASE_URL`, `DB_PATH`
- `SENDER_EMAIL`, `SENDER_PASSWORD`
- `ADMIN_PASSWORD`
- `MAX_HISTORY`, `CHUNK_SIZE`

## Adding New Features

1. **New Tool**: Create in tools.py
2. **New Intent**: Add to constants.py, update chat_logic.py
3. **New Booking Type**: Add to BOOKING_TYPES in constants.py
4. **New Database Field**: Update models.py
5. **New Admin Feature**: Update admin_dashboard.py

## Testing Files

To test individual components:

```python
# Test models
python -c "from models import init_db; init_db(); print('DB OK')"

# Test LLM
python -c "from llm import get_chat_model; m = get_chat_model(); print('LLM OK')"

# Test embeddings
python -c "from embeddings import get_embeddings_model; e = get_embeddings_model(); print('Embeddings OK')"
```

## Cleanup & Maintenance

### Clear Database
```bash
rm bookings.db
python -c "from models import init_db; init_db()"
```

### Clear Vector Store
```bash
rm -rf vector_store/
```

### Clear Logs
```bash
rm -rf logs/
```

### Clear Cache
```bash
rm -rf __pycache__
find . -type d -name __pycache__ -delete
```

## Performance Notes

- main.py: Streamlit overhead ~1-2s per page load
- llm.py: Model response time varies (Groq: fast, OpenAI: slower)
- rag_pipeline.py: PDF processing ~5-10s per 10MB
- models.py: DB queries <100ms typically
- admin_dashboard.py: Renders ~1000 bookings easily

## Security Considerations

- **Secrets**: Never commit .env file
- **Logs**: Contain sensitive info, restrict access
- **Database**: Use strong passwords for PostgreSQL
- **Email**: Use app passwords, not real passwords
- **Admin**: Change default admin password
