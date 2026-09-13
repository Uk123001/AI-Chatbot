"""
Multi-provider LLM access. Picks a provider based on LLM_PROVIDER, falling
back to whichever API key is actually available. Supports Groq, OpenAI, and
Google Gemini via LangChain chat model wrappers so the rest of the codebase
only ever talks to a single `.invoke(messages)` interface.
"""
from functools import lru_cache
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.config import settings


def _build_groq():
    from langchain_groq import ChatGroq
    return ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL, temperature=0.3)


def _build_openai():
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL, temperature=0.3)


def _build_gemini():
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(google_api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL, temperature=0.3)


_BUILDERS = {
    "groq": (_build_groq, lambda: bool(settings.GROQ_API_KEY)),
    "openai": (_build_openai, lambda: bool(settings.OPENAI_API_KEY)),
    "gemini": (_build_gemini, lambda: bool(settings.GEMINI_API_KEY)),
}


@lru_cache(maxsize=1)
def get_llm():
    """Return a cached chat model instance for the configured/available provider."""
    order = [settings.LLM_PROVIDER] + [p for p in _BUILDERS if p != settings.LLM_PROVIDER]
    for provider in order:
        builder, has_key = _BUILDERS.get(provider, (None, None))
        if builder and has_key():
            return builder()
    raise RuntimeError(
        "No LLM API key configured. Set GROQ_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY "
        "in your .env file."
    )


def active_provider_name() -> str:
    order = [settings.LLM_PROVIDER] + [p for p in _BUILDERS if p != settings.LLM_PROVIDER]
    for provider in order:
        _, has_key = _BUILDERS.get(provider, (None, None))
        if has_key and has_key():
            return provider
    return "none"


def chat(system_prompt: str, history: list, user_message: str) -> str:
    """
    Send a system prompt + trimmed conversation history + latest user message
    to the active LLM and return plain text.
    `history` is a list of {"role": "user"|"assistant", "content": str}.
    """
    try:
        llm = get_llm()
    except RuntimeError as exc:
        return f"⚠️ {exc}"

    messages = [SystemMessage(content=system_prompt)]
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=user_message))

    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as exc:
        return f"I ran into a problem reaching the language model ({exc}). Please try again in a moment."
