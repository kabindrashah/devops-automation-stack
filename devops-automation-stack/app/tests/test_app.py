import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import TASKS, app  # noqa: E402


def client():
    TASKS.clear()
    return app.test_client()


def test_health():
    r = client().get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_create_and_list_task():
    c = client()
    r = c.post("/tasks", json={"title": "write README"})
    assert r.status_code == 201
    assert c.get("/tasks").get_json()[0]["title"] == "write README"


def test_create_task_requires_title():
    assert client().post("/tasks", json={}).status_code == 400


def test_boom_returns_500():
    assert client().get("/boom").status_code == 500


def test_metrics_exposed():
    c = client()
    c.get("/health")
    body = c.get("/metrics").get_data(as_text=True)
    assert "app_requests_total" in body
