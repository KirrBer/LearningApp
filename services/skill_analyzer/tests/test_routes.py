import pytest
from fastapi.testclient import TestClient
from skill_analyzer.main import app
from skill_analyzer.exceptions import ModelInferenceError, PDFExtractionError, DatabaseError


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # prevent heavy model loading
    from skill_analyzer.model_manager import model_manager
    from skill_analyzer.threadpool import threadpool_manager

    monkeypatch.setattr(model_manager, "load_models", lambda: None)
    monkeypatch.setattr(model_manager, "unload_models", lambda: None)

    # Initialize threadpool_manager for testing
    threadpool_manager.create()

    monkeypatch.setattr("skill_analyzer.routes.extract_skills_from_text", lambda text: ["x"])
    
    async def fake_extract_pdf(file):
        return "some text"
    monkeypatch.setattr("skill_analyzer.routes.extract_text_from_pdf", fake_extract_pdf)

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


# Exception handling tests
def test_post_text_with_empty_text():
    """Test error handling for empty text input."""
    client = TestClient(app)
    resp = client.post("/extract_skills_from_text", json={"text": ""})
    assert resp.status_code == 400
    assert "cannot be empty" in resp.json()["detail"].lower()


def test_post_text_with_whitespace_only():
    """Test error handling for whitespace-only text."""
    client = TestClient(app)
    resp = client.post("/extract_skills_from_text", json={"text": "   \n  \t  "})
    assert resp.status_code == 400


def test_post_pdf_with_invalid_content_type(monkeypatch):
    """Test error handling for non-PDF files."""
    client = TestClient(app)
    resp = client.post(
        "/extract_skills_from_pdf",
        files={"file": ("document.txt", b"data", "text/plain")},
    )
    assert resp.status_code == 400
    assert "pdf" in resp.json()["detail"].lower()


def test_post_pdf_no_file():
    """Test error handling when no file is provided."""
    client = TestClient(app)
    resp = client.post("/extract_skills_from_pdf")
    assert resp.status_code == 422  # Unprocessable entity (missing required field)






