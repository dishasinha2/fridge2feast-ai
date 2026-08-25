"""Unit tests for the shared Gemini client boundary; no network calls are made."""
import pytest

from services import gemini_client


class FakeModels:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return type("Response", (), {"text": response})()


def test_missing_api_key_is_rejected_without_exposing_a_secret(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(gemini_client, "get_gemini_api_key", lambda: "")
    gemini_client.get_gemini_client.cache_clear()

    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        gemini_client.get_gemini_client()


def test_request_uses_one_sdk_attempt_and_a_strict_timeout():
    models = FakeModels(['{"ok": true}'])
    client = type("Client", (), {"models": models})()

    result = gemini_client.generate_json_content(
        "hello", temperature=0.1, primary_model="gemini-3.6-flash",
        fallback_model=None, request_timeout_ms=12_345, client=client,
    )

    assert result == '{"ok": true}'
    config = models.calls[0]["config"]
    assert config.http_options.timeout == 12_345
    assert config.http_options.retry_options.attempts == 1


def test_one_distinct_fallback_is_attempted_after_primary_failure():
    models = FakeModels([RuntimeError("primary unavailable"), '{"ok": true}'])
    client = type("Client", (), {"models": models})()

    result = gemini_client.generate_json_content(
        "hello", temperature=0.1, primary_model="gemini-3.6-flash",
        fallback_model="gemini-3.6-flash-backup", client=client,
    )

    assert result == '{"ok": true}'
    assert [call["model"] for call in models.calls] == ["gemini-3.6-flash", "gemini-3.6-flash-backup"]
