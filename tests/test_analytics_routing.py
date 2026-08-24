"""Focused tests for the authenticated Analytics route."""
from types import SimpleNamespace

from components import analytics
import app


class SessionState(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def test_authenticated_user_routes_to_existing_analytics_component(monkeypatch):
    calls = []
    state = SessionState(authenticated_user=SimpleNamespace(id=7), current_page="analytics")
    monkeypatch.setattr(app.st, "session_state", state)
    monkeypatch.setattr(app, "render_top_navigation", lambda: None)
    monkeypatch.setattr(app, "render_analytics_component", lambda: calls.append("analytics"))

    app.main()

    assert calls == ["analytics"]


def test_unauthenticated_user_cannot_route_to_analytics(monkeypatch):
    calls = []
    state = SessionState(authenticated_user=None, current_page="analytics")
    monkeypatch.setattr(app.st, "session_state", state)
    monkeypatch.setattr(app, "render_landing", lambda: calls.append("landing"))

    app.main()

    assert state.current_page == "landing"
    assert calls == ["landing"]


def test_analytics_route_uses_existing_renderer_without_gemini(monkeypatch):
    calls = []
    monkeypatch.setattr(analytics, "load_analytics_data", lambda user_id: calls.append(user_id) or {
        "inventory": analytics.inventory_to_freshness_df([]),
        "insights": analytics.kitchen_insight_frames(analytics.inventory_to_freshness_df([])),
        "saved_recipes": [],
        "cooking_history": [],
    })
    monkeypatch.setattr(analytics.st, "session_state", SessionState(authenticated_user=SimpleNamespace(id=11)))
    monkeypatch.setattr(analytics.st, "info", lambda message: calls.append(message))

    analytics.render_analytics_component()

    assert calls[0] == 11
    assert any("Not enough data yet" in str(call) for call in calls)