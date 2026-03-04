import pytest
from fastapi.testclient import TestClient
from skill_analyzer.main import app


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # prevent heavy model loading
    from skill_analyzer.model_manager import model_manager

    monkeypatch.setattr(model_manager, "load_models", lambda: None)
    monkeypatch.setattr(model_manager, "unload_models", lambda: None)

    monkeypatch.setattr("skill_analyzer.routes.extract_skills_from_text", lambda text: ["x"])
    
    async def fake_extract_pdf(file):
        return ["x"]
    monkeypatch.setattr("skill_analyzer.routes.extract_skills_from_pdf", fake_extract_pdf)

    async def fake_find(skills):
        return [{"name": skills[0], "course": None}]

    monkeypatch.setattr("skill_analyzer.routes.find_courses", fake_find)


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
