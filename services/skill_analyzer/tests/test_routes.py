import pytest
from fastapi.testclient import TestClient
from skill_analyzer.main import app


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # prevent heavy model loading
    from skill_analyzer.model_manager import model_manager
    from skill_analyzer import utils

    monkeypatch.setattr(model_manager, "load_models", lambda: None)
    monkeypatch.setattr(model_manager, "unload_models", lambda: None)

    # stub util functions used by the endpoints
    monkeypatch.setattr(utils, "extract_skills_from_text", lambda text: ["x"])
    monkeypatch.setattr(utils, "extract_skills_from_pdf", lambda file: ["x"])

    async def fake_find(skills):
        return [{"name": skills[0], "course": None}]

    monkeypatch.setattr(utils, "find_courses", fake_find)


def test_post_text():
    client = TestClient(app)
    resp = client.post("/extract_skills_from_text", json={"text": "hello"})
    assert resp.status_code == 200
    assert resp.json() == [{"name": "x", "course": None}]


def test_post_pdf():
    client = TestClient(app)
    resp = client.post(
        "/extract_skills_from_pdf",
        files={"file": ("resume.pdf", b"data", "application/pdf")},
    )
    assert resp.status_code == 200
    assert resp.json() == [{"name": "x", "course": None}]
