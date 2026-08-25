"""Official Google Gemini Client wrapper for Fridge2Feast AI."""
import os
import logging
from functools import lru_cache
from typing import Any, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
DEFAULT_REQUEST_TIMEOUT_MS = 20_000

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
    max_output_tokens: Optional[int] = None,
    primary_model: str = "gemini-flash-latest",
    fallback_model: Optional[str] = "gemini-flash-lite-latest",
    request_timeout_ms: int = DEFAULT_REQUEST_TIMEOUT_MS,
    client: Optional[Any] = None,
) -> str:
    """Generate JSON with the one shared Gemini boundary used by AI services.

    Each model request uses one SDK attempt and a strict timeout. A caller may
    opt into one distinct fallback model; no hidden SDK retries are allowed.
    """
    client = client or get_gemini_client()
    if hasattr(client, "models") and hasattr(client.models, "generate_content"):
        try:
            from google.genai import types
            http_options = types.HttpOptions(
                timeout=request_timeout_ms,
                retry_options=types.HttpRetryOptions(attempts=1),
            )
            config_values = {
                "temperature": temperature,
                "response_mime_type": "application/json",
                "http_options": http_options,
                # This app never supplies callable tools. Disabling AFC avoids
                # the SDK's deprecated Models.generate_content AFC path.
                "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True),
            }
            if max_output_tokens is not None:
                config_values["max_output_tokens"] = max_output_tokens
            config: Any = types.GenerateContentConfig(**config_values)
        except ImportError:
            config = {
                "temperature": temperature,
                "response_mime_type": "application/json",
                "http_options": {"timeout": request_timeout_ms, "retry_options": {"attempts": 1}},
                "automatic_function_calling": {"disable": True},
            }
            if max_output_tokens is not None:
                config["max_output_tokens"] = max_output_tokens

        try:
            logger.info("Gemini request starting model=%s timeout_ms=%d", primary_model, request_timeout_ms)
            response = client.models.generate_content(
                model=primary_model, contents=contents, config=config
            )
        except Exception as primary_error:
            if not fallback_model or fallback_model == primary_model:
                raise
            logger.warning(
                "Gemini request failed model=%s error=%s; trying one fallback model=%s",
                primary_model,
                type(primary_error).__name__,
                fallback_model,
            )
            logger.info("Gemini request starting model=%s timeout_ms=%d", fallback_model, request_timeout_ms)
            response = client.models.generate_content(
                model=fallback_model, contents=contents, config=config
            )
        response_model = fallback_model if 'primary_error' in locals() else primary_model
        logger.info("Gemini response received model=%s", response_model)
        response_text = str(getattr(response, "text", "") or "")
        logger.info(
            "Gemini response text extraction completed model=%s response_length=%d",
            response_model,
            len(response_text),
        )
        return response_text

    # Compatibility for installations still using google-generativeai.
    model = client.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(contents)
    return str(getattr(response, "text", "") or "")
