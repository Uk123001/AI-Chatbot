from langchain.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import config


def get_chat_model():
    """Get chat model based on configuration"""
    
    if config.LLM_PROVIDER.lower() == "groq":
        return get_groq_model()
    elif config.LLM_PROVIDER.lower() == "openai":
        return get_openai_model()
    elif config.LLM_PROVIDER.lower() == "google":
        return get_google_model()
    else:
        raise ValueError(f"Unknown LLM provider: {config.LLM_PROVIDER}")


def get_groq_model():
    """Initialize Groq chat model"""
    if not config.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in environment variables")
    
    model = ChatGroq(
        api_key=config.GROQ_API_KEY,
        model_name=config.LLM_MODEL,
        temperature=0.7,
        max_tokens=1024
    )
    return model


def get_openai_model():
    """Initialize OpenAI chat model"""
    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in environment variables")
    
    model = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model_name=config.LLM_MODEL,
        temperature=0.7,
        max_tokens=1024
    )
    return model


def get_google_model():
    """Initialize Google Gemini chat model"""
    if not config.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not set in environment variables")
    
    model = ChatGoogleGenerativeAI(
        api_key=config.GOOGLE_API_KEY,
        model=config.LLM_MODEL,
        temperature=0.7,
        max_tokens=1024
    )
    return model


def get_chatgroq_model():
    """Get Groq model (fallback for compatibility)"""
    try:
        return get_groq_model()
    except:
        return None
