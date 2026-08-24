"""Official Google Gemini Client wrapper for Fridge2Feast AI."""
import os
import logging
from functools import lru_cache
from typing import Any, Optional

logger = logging.getLogger(__name__)

def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from environment or Streamlit secrets safely."""
    # 1. Check os.environ
    key = os.environ.get("GEMINI_API_KEY", "")
    if key and key != "MY_GEMINI_API_KEY":
        return key
    
    # 2. Check streamlit secrets if available
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = st.secrets["GEMINI_API_KEY"]
            if key and key != "MY_GEMINI_API_KEY":
                return key
    except Exception:
        pass

    return os.environ.get("GEMINI_API_KEY", "")

@lru_cache(maxsize=1)
def get_gemini_client():
    """
    Instantiate the official Google GenAI client.
    Returns the client instance or raises an error if API key is missing.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=api_key)
            return legacy_genai
        except Exception as e:
            raise ImportError(f"Google GenAI SDK is not installed: {e}")


def generate_json_content(
    contents: Any,
    *,
    temperature: float,
    primary_model: str = "gemini-flash-latest",
    fallback_model: str = "gemini-flash-lite-latest",
    client: Optional[Any] = None,
) -> str:
    """Generate JSON with the one shared Gemini boundary used by AI services.

    This intentionally does not retry arbitrary failures: a single fallback model is
    enough to improve availability without multiplying requests on a Streamlit rerun.
    Callers invoke it only from explicit user actions and translate errors for the UI.
    """
    client = client or get_gemini_client()
    if hasattr(client, "models") and hasattr(client.models, "generate_content"):
        try:
            from google.genai import types
            config: Any = types.GenerateContentConfig(
                temperature=temperature, response_mime_type="application/json"
            )
        except ImportError:
            config = {"temperature": temperature, "response_mime_type": "application/json"}

        try:
            response = client.models.generate_content(
                model=primary_model, contents=contents, config=config
            )
        except Exception as primary_error:
            logger.warning(
                "Gemini primary model unavailable; trying configured fallback (%s)",
                type(primary_error).__name__,
            )
            response = client.models.generate_content(
                model=fallback_model, contents=contents, config=config
            )
        return str(getattr(response, "text", "") or "")

    # Compatibility for installations still using google-generativeai.
    model = client.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(contents)
    return str(getattr(response, "text", "") or "")
