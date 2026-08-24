"""Unit tests for the shared Gemini client boundary; no network calls are made."""
import pytest

from services import gemini_client


def test_missing_api_key_is_rejected_without_exposing_a_secret(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(gemini_client, "get_gemini_api_key", lambda: "")
    gemini_client.get_gemini_client.cache_clear()

    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        gemini_client.get_gemini_client()
