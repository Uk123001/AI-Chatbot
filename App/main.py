import streamlit as st
import os
import sys
from pathlib import Path

# Add project root and all sibling module folders to path.
# Each module (config, llm, chat_logic, models, tools, ...) lives in its own
# folder (App/, LLM/, Admin/, Tools/, Database/) and imports its neighbors
# with flat `import x` statements, so every one of those folders must be on
# sys.path - just adding App/ (this file's folder) is not enough.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
for _sub in ("App", "LLM", "Admin", "Tools", "Database"):
    _path = str(_PROJECT_ROOT / _sub)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import config
from llm import get_chat_model
from chat_logic import ChatLogic, BookingFlowManager
from rag_pipeline import RAGPipeline
from admin_dashboard import admin_dashboard
from tools import RAGTool, BookingPersistenceTool, EmailTool, get_tools
from models import init_db
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_logic" not in st.session_state:
        st.session_state.chat_logic = ChatLogic()
    
    if "booking_flow" not in st.session_state:
        st.session_state.booking_flow = BookingFlowManager()
    
    if "rag_pipeline" not in st.session_state:
        st.session_state.rag_pipeline = RAGPipeline()
    
    if "chat_model" not in st.session_state:
        try:
            st.session_state.chat_model = get_chat_model()
        except Exception as e:
            st.session_state.chat_model = None
            st.session_state.model_error = str(e)
    
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False


def get_chat_response(messages, system_prompt, rag_pipeline=None):
    """Get response from chat model"""
    try:
        if st.session_state.chat_model is None:
            return "Error: Chat model not initialized. Please check API keys."
        
        # Prepare messages for the model
        formatted_messages = [SystemMessage(content=system_prompt)]
        
        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            else:
                formatted_messages.append(AIMessage(content=msg["content"]))
        
        # Get response from model
        response = st.session_state.chat_model.invoke(formatted_messages)
        return response.content
    
    except Exception as e:
        return f"Error getting response: {str(e)}"


def chat_page():
    """Main chat interface"""
    st.title("🤖 AI Booking Assistant")
    
    # Create two columns
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.booking_flow.reset()
            st.rerun()
    
    # Display status
    if st.session_state.chat_model is None:
        st.error(f"⚠️ Model Error: {st.session_state.get('model_error', 'Unknown error')}")
        st.info("Please configure API keys in environment variables:")
        st.code("GROQ_API_KEY=your_key", language="bash")
        return
    
    # PDF Upload Section
    st.subheader("📄 Upload Booking Documents")
    uploaded_file = st.file_uploader("Upload PDF for RAG", type="pdf")
    
    if uploaded_file is not None:
        with st.spinner("Processing PDF..."):
            # Save temporary file
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Ingest PDF
            chunks, message = st.session_state.rag_pipeline.ingest_pdf(temp_path)
            
            if chunks > 0:
                st.success(f"✅ {message} ({chunks} chunks extracted)")
            else:
                st.error(f"❌ {message}")
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    # Chat interface
    st.subheader("💬 Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.chat_logic.add_to_memory("user", prompt)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                system_prompt = st.session_state.chat_logic.get_system_prompt()
                response = get_chat_response(
                    st.session_state.messages,
                    system_prompt,
                    st.session_state.rag_pipeline
                )
                
                # Add to memory and chat history
                st.session_state.chat_logic.add_to_memory("assistant", response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                st.markdown(response)


def instructions_page():
    """Instructions and setup page"""
    st.title("📖 Getting Started with AI Booking Assistant")
    
    st.markdown("""
    ## Welcome! 👋
    
    The AI Booking Assistant is a smart chatbot that helps manage bookings for various services
    (doctors, salons, hotels, events, classes, etc.).
    
    ### Features
    
    ✅ **Conversational Booking** - Natural dialogue to collect booking details
    ✅ **RAG Enabled** - Upload PDFs for context-aware responses
    ✅ **Database Storage** - All bookings saved in SQLite/Supabase
    ✅ **Email Confirmation** - Automatic booking confirmation emails
    ✅ **Admin Dashboard** - View and manage all bookings
    
    ### Setup Instructions
    
    #### 1. API Key Configuration
    
    Set the following environment variables:
    
    **Option A: Groq (Recommended)**
    ```bash
    export GROQ_API_KEY=your_groq_api_key
    export LLM_PROVIDER=groq
    export LLM_MODEL=mixtral-8x7b-32768
    ```
    
    **Option B: OpenAI**
    ```bash
    export OPENAI_API_KEY=your_openai_key
    export LLM_PROVIDER=openai
    export LLM_MODEL=gpt-4o-mini
    ```
    
    **Option C: Google Gemini**
    ```bash
    export GOOGLE_API_KEY=your_google_key
    export LLM_PROVIDER=google
    export LLM_MODEL=gemini-1.5-flash
    ```
    
    #### 2. Email Configuration (Optional)
    
    ```bash
    export SENDER_EMAIL=your_email@gmail.com
    export SENDER_PASSWORD=your_app_password
    export SMTP_SERVER=smtp.gmail.com
    export SMTP_PORT=587
    ```
    
    #### 3. Database Configuration
    
    ```bash
    export DB_PATH=bookings.db
    export DATABASE_URL=sqlite:///bookings.db
    ```
    
    ### How to Use
    
    1. **Go to Chat** - Start a conversation with the bot
    2. **Upload PDFs** - Add documents for RAG context
    3. **Make Bookings** - The bot will guide you through the booking process
    4. **Admin Dashboard** - View all bookings (Password: admin123)
    
    ### Booking Flow
    
    The chatbot will:
    1. Detect booking intent
    2. Ask for missing information (name, email, phone, type, date, time)
    3. Summarize your details
    4. Ask for confirmation
    5. Save to database and send confirmation email
    6. Provide booking ID
    
    ### Supported Booking Types
    
    - 👨‍⚕️ Doctor
    - 💇 Salon
    - 🏨 Hotel
    - 🎉 Events
    - 📚 Classes
    - 🍽️ Restaurant
    - 💪 Gym
    - 🧖 Spa
    
    ### Tips
    
    - Be natural in your conversation
    - Provide information as you have it
    - Dates should be in YYYY-MM-DD format
    - Times should be in HH:MM format (24-hour)
    - Check your email for booking confirmation
    
    ### Support
    
    For issues or questions, please check:
    - API key configuration
    - Email settings for confirmation
    - Database connectivity
    
    Happy Booking! 🎉
    """)


def main():
    """Main application"""
    # Configure page
    st.set_page_config(**config.PAGE_CONFIG)
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
    
    # Navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Go to:",
            ["Chat", "Instructions", "Admin Dashboard"],
            index=0
        )
    
    # Route to appropriate page
    if page == "Chat":
        chat_page()
    elif page == "Instructions":
        instructions_page()
    elif page == "Admin Dashboard":
        admin_dashboard()


if __name__ == "__main__":
    main()
