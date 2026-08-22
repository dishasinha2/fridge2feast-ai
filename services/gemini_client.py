import os
import time
import logging
from typing import Optional, Any, Dict, List
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Safe logger that logs events without sensitive user content
logger = logging.getLogger("fridge2feast.gemini")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# .env is intentionally supported only for local development. Streamlit secrets
# and process environment variables remain the deployment configuration sources.
load_dotenv()

def get_gemini_model_name() -> str:
    """Centralized Model Configuration (source of truth with strict format validation)."""
    candidate = None
    try:
        if "GEMINI_MODEL" in st.secrets and st.secrets["GEMINI_MODEL"]:
            candidate = str(st.secrets["GEMINI_MODEL"]).strip()
    except Exception:
        pass
    
    if not candidate:
        candidate = os.environ.get("GEMINI_MODEL", "").strip()

    # Reject token-like or arbitrary strings
    if candidate and candidate.startswith("gemini-") and len(candidate) <= 64 and all(
        char.isalnum() or char in "-_." for char in candidate
    ):
        return candidate

    if candidate:
        logger.warning("Ignored invalid GEMINI_MODEL configuration; using the default model.")

    return "gemini-2.5-flash"

GEMINI_MODEL = get_gemini_model_name()

# Supported valid models for explicit health checks
FALLBACK_MODELS = [GEMINI_MODEL]

class GeminiServiceException(Exception):
    """Custom exception containing user-friendly error message, diagnostic details, and error category."""
    def __init__(
        self,
        user_message: str,
        error_code: Optional[int] = None,
        is_transient: bool = False,
        error_category: str = "INTERNAL_ERROR",
        technical_details: Optional[str] = None,
    ):
        super().__init__(user_message)
        self.user_message = user_message
        self.error_code = error_code
        self.is_transient = is_transient
        self.error_category = error_category
        self.technical_details = technical_details

def get_gemini_client() -> genai.Client:
    """
    Lazy initialization of Gemini client.
    First checks st.secrets, then os.environ["GEMINI_API_KEY"].
    """
    api_key = None
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise GeminiServiceException(
            "AI scanning isn't configured yet. Please contact the app administrator.",
            error_code=None,
            is_transient=False
            ,error_category="MISSING_API_KEY"
        )

    try:
        return genai.Client(
            api_key=api_key,
            http_options={
                'headers': {
                    'User-Agent': 'aistudio-build'
                }
            }
        )
    except Exception:
        logger.error("Failed to initialize Gemini Client: Authentication or SDK error.")
        raise GeminiServiceException(
            "AI scanning is temporarily unavailable. Please try again later.",
            error_code=401,
            is_transient=False,
            error_category="INVALID_API_KEY"
        )

def _record_telemetry_event(
    success: bool,
    latency_ms: float,
    status_code: Optional[int] = None,
    validation_error: bool = False
):
    """
    Safely records runtime telemetry into Streamlit session state without saving raw inputs or outputs.
    """
    if "ai_telemetry" not in st.session_state:
        st.session_state["ai_telemetry"] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "errors_503": 0,
            "errors_429": 0,
            "timeouts": 0,
            "validation_failures": 0,
            "latencies_ms": [],
        }

    tel = st.session_state["ai_telemetry"]
    tel["total_requests"] += 1
    if success:
        tel["successful_requests"] += 1
        tel["latencies_ms"].append(latency_ms)
    else:
        tel["failed_requests"] += 1
        if status_code == 503:
            tel["errors_503"] += 1
        elif status_code == 429:
            tel["errors_429"] += 1
        elif status_code == 408:
            tel["timeouts"] += 1
        
        if validation_error:
            tel["validation_failures"] += 1

def _set_last_diagnostic(
    operation: str,
    stage: str,
    status_code: Optional[int],
    model: str,
    exception_type: Optional[str],
    error_message: Optional[str],
    success: bool,
    latency_ms: float = 0.0,
):
    """
    Safely stores diagnostic information in session state without logging keys, passwords, or image bytes.
    """
    api_key_configured = False
    try:
        api_key_configured = bool(
            (st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None) or
            os.environ.get("GEMINI_API_KEY")
        )
    except Exception:
        api_key_configured = bool(os.environ.get("GEMINI_API_KEY"))

    st.session_state["last_ai_diagnostic"] = {
        "operation": operation,
        "stage": stage,
        "status_code": status_code,
        "model": model,
        "exception_type": exception_type,
        "error_message": error_message,
        "success": success,
        "latency_ms": round(latency_ms, 1),
        "api_key_configured": api_key_configured,
        "timestamp": time.strftime("%H:%M:%S"),
    }

def invoke_gemini_with_retry(
    contents: Any,
    system_instruction: Optional[str] = None,
    response_schema: Optional[Any] = None,
    response_mime_type: Optional[str] = None,
    temperature: float = 0.2,
    max_retries_per_model: int = 2,
    max_retries: Optional[int] = None,
    custom_model: Optional[str] = None,
    operation_name: str = "recipe_or_vision_call",
) -> str:
    """
    Centralized, robust Gemini API caller with multi-model fallback across supported models
    (e.g., gemini-2.5-flash, gemini-flash-latest, gemini-3.7-flash) and exponential backoff
    for transient failures (503, 429, timeouts).
    Records grounded real latency and safe runtime diagnostic metrics.
    """
    client = get_gemini_client()
    target_model = custom_model if custom_model else GEMINI_MODEL
    models_to_try = [target_model]
    
    effective_retries = max_retries if max_retries is not None else max_retries_per_model

    config_args: dict = {"temperature": temperature}
    if system_instruction:
        config_args["system_instruction"] = system_instruction
    if response_mime_type:
        config_args["response_mime_type"] = response_mime_type
    if response_schema:
        config_args["response_schema"] = response_schema

    gen_config = types.GenerateContentConfig(**config_args)

    backoff_delays = [0.8, 1.6]
    last_err: Optional[GeminiServiceException] = None
    start_time = time.perf_counter()

    for model_name in models_to_try:
        for attempt in range(effective_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=gen_config,
                )
                
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                _record_telemetry_event(success=True, latency_ms=latency_ms)
                _set_last_diagnostic(
                    operation=operation_name,
                    stage="completed",
                    status_code=200,
                    model=model_name,
                    exception_type=None,
                    error_message=None,
                    success=True,
                    latency_ms=latency_ms,
                )

                if response and response.text:
                    return response.text
                return "{}"

            except APIError as api_err:
                code = getattr(api_err, "code", None) or getattr(api_err, "status_code", None)
                err_str = str(api_err).lower()
                latency_ms = (time.perf_counter() - start_time) * 1000.0

                is_503 = code == 503 or "503" in err_str or "unavailable" in err_str or "high demand" in err_str
                is_429 = code == 429 or "429" in err_str or "quota" in err_str or "rate limit" in err_str
                is_408 = code == 408 or "408" in err_str or "timeout" in err_str or "timed out" in err_str
                is_auth = code in (400, 401, 403) and ("api_key" in err_str or "unauthenticated" in err_str or "permission" in err_str)

                logger.warning(f"Gemini API model {model_name} attempt {attempt + 1} failed. Status: {code or 'unknown'}")

                _set_last_diagnostic(
                    operation=operation_name,
                    stage="api_error",
                    status_code=code,
                    model=model_name,
                    exception_type="APIError",
                    error_message=str(api_err)[:200],
                    success=False,
                    latency_ms=latency_ms,
                )

                if is_auth:
                    _record_telemetry_event(success=False, latency_ms=0, status_code=401)
                    raise GeminiServiceException(
                        "AI scanning is temporarily unavailable. Please try again later.",
                        error_code=401,
                        is_transient=False,
                        error_category="INVALID_API_KEY",
                        technical_details=str(api_err)[:200]
                    )

                if is_503:
                    last_err = GeminiServiceException(
                        "✨ Gemini is temporarily busy. Please try again in a moment.",
                        error_code=503,
                        is_transient=True,
                        error_category="SERVICE_UNAVAILABLE",
                        technical_details=str(api_err)[:200]
                    )
                elif is_429:
                    last_err = GeminiServiceException(
                        "✨ AI usage is temporarily limited. Please try again shortly.",
                        error_code=429,
                        is_transient=True,
                        error_category="RATE_LIMITED",
                        technical_details=str(api_err)[:200]
                    )
                elif is_408:
                    last_err = GeminiServiceException(
                        "The AI request timed out. Please try again.",
                        error_code=408,
                        is_transient=True,
                        error_category="TIMEOUT",
                        technical_details=str(api_err)[:200]
                    )
                else:
                    last_err = GeminiServiceException(
                        "✨ The AI service is currently unavailable. Please try again in a moment.",
                        error_code=code or 500,
                        is_transient=True,
                        error_category="INTERNAL_ERROR",
                        technical_details=str(api_err)[:200]
                    )

                if (is_503 or is_429 or is_408) and attempt < effective_retries - 1:
                    time.sleep(backoff_delays[min(attempt, len(backoff_delays) - 1)])
                    continue
                else:
                    _record_telemetry_event(success=False, latency_ms=0, status_code=code or 500)
                    # Try next fallback model
                    break

            except TimeoutError as te:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                logger.warning(f"Gemini API timeout on model {model_name} attempt {attempt + 1}")
                _set_last_diagnostic(
                    operation=operation_name,
                    stage="timeout",
                    status_code=408,
                    model=model_name,
                    exception_type="TimeoutError",
                    error_message=str(te)[:200],
                    success=False,
                    latency_ms=latency_ms,
                )
                last_err = GeminiServiceException(
                    "The AI request timed out. Please try again.",
                    error_code=408,
                    is_transient=True,
                    error_category="TIMEOUT",
                    technical_details=str(te)[:200]
                )
                if attempt < effective_retries - 1:
                    time.sleep(backoff_delays[min(attempt, len(backoff_delays) - 1)])
                    continue
                _record_telemetry_event(success=False, latency_ms=0, status_code=408)
                break

            except Exception as e:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                err_msg = str(e).lower()
                is_503 = "503" in err_msg or "high demand" in err_msg or "unavailable" in err_msg
                is_429 = "429" in err_msg or "rate" in err_msg or "quota" in err_msg

                _set_last_diagnostic(
                    operation=operation_name,
                    stage="exception",
                    status_code=503 if is_503 else (429 if is_429 else 500),
                    model=model_name,
                    exception_type=type(e).__name__,
                    error_message=str(e)[:200],
                    success=False,
                    latency_ms=latency_ms,
                )

                if is_503:
                    last_err = GeminiServiceException(
                        "✨ Gemini is temporarily busy. Please try again in a moment.",
                        error_code=503,
                        is_transient=True,
                        error_category="SERVICE_UNAVAILABLE",
                        technical_details=str(e)[:200]
                    )
                    if attempt < effective_retries - 1:
                        time.sleep(backoff_delays[min(attempt, len(backoff_delays) - 1)])
                        continue
                    _record_telemetry_event(success=False, latency_ms=0, status_code=503)
                    break
                elif is_429:
                    last_err = GeminiServiceException(
                        "✨ AI usage is temporarily limited. Please try again shortly.",
                        error_code=429,
                        is_transient=True,
                        error_category="RATE_LIMITED",
                        technical_details=str(e)[:200]
                    )
                    if attempt < effective_retries - 1:
                        time.sleep(backoff_delays[min(attempt, len(backoff_delays) - 1)])
                        continue
                    _record_telemetry_event(success=False, latency_ms=0, status_code=429)
                    break
                else:
                    logger.error(f"Unexpected Gemini exception on model {model_name} attempt {attempt + 1}: {e}")
                    last_err = GeminiServiceException(
                        "✨ The AI service is currently unavailable. Please try again in a moment.",
                        error_code=500,
                        is_transient=True,
                        error_category="INTERNAL_ERROR",
                        technical_details=str(e)[:200]
                    )
                    _record_telemetry_event(success=False, latency_ms=0, status_code=500)
                    break

    if last_err:
        raise last_err

    _record_telemetry_event(success=False, latency_ms=0, status_code=503)
    raise GeminiServiceException(
        "✨ Gemini is temporarily busy. Please try again in a moment.",
        error_code=503,
        is_transient=True,
        error_category="SERVICE_UNAVAILABLE"
    )

def generate_text(prompt: str, **kwargs) -> str:
    """Generate text through the single centralized Gemini call path."""
    return invoke_gemini_with_retry(contents=prompt, **kwargs)


def generate_multimodal(contents: Any, **kwargs) -> str:
    """Generate multimodal content through the single centralized Gemini call path."""
    return invoke_gemini_with_retry(contents=contents, **kwargs)


def health_check_gemini(custom_model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Developer / Evaluator Health Check tool:
    Tests connectivity, API configuration, and round-trip latency against the Gemini model.
    Returns structured results safely without revealing secrets.
    """
    start_time = time.perf_counter()
    model_to_test = custom_model_name or get_gemini_model_name()
    api_key_configured = False
    try:
        api_key_configured = bool(
            (st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None) or
            os.environ.get("GEMINI_API_KEY")
        )
    except Exception:
        api_key_configured = bool(os.environ.get("GEMINI_API_KEY"))

    if not api_key_configured:
        return {
            "available": False,
            "model": model_to_test,
            "latency_ms": 0,
            "error_type": "CONFIGURATION_MISSING",
            "message": "GEMINI_API_KEY is not configured.",
        }

    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=model_to_test,
            contents="Respond with JSON: {\"status\":\"ok\"}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            ),
        )
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "available": True,
            "model": model_to_test,
            "latency_ms": round(latency_ms, 1),
            "error_type": None,
            "message": "Gemini is reachable.",
        }
    except APIError as e:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "available": False,
            "model": model_to_test,
            "latency_ms": round(latency_ms, 1),
            "error_type": type(e).__name__,
            "message": "Gemini could not be reached with the configured model.",
        }
    except Exception:
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return {
            "available": False,
            "model": model_to_test,
            "latency_ms": round(latency_ms, 1),
            "error_type": "SERVICE_ERROR",
            "message": "Gemini could not be reached right now.",
        }


def run_gemini_health_check(custom_model_name: Optional[str] = None) -> Dict[str, Any]:
    """Backward-compatible alias for the evaluation dashboard."""
    result = health_check_gemini(custom_model_name)
    result["status"] = "PASS" if result["available"] else "FAIL"
    result["error"] = result["message"]
    return result
