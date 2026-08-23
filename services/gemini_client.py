"""Official Google Gemini Client wrapper for Fridge2Feast AI."""
import os
import logging
from typing import Optional, Any

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
