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

    # Mock kafka_manager
    class FakeProducer:
        async def send(self, topic, value):
            pass  # Do nothing in tests

    class FakeKafkaManager:
        def __init__(self):
            self.producer = FakeProducer()

    monkeypatch.setattr("skill_analyzer.routes.kafka_manager", FakeKafkaManager())


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


def test_post_text_model_error(monkeypatch):
    """Test error handling when model inference fails."""
    def failing_extract(text):
        raise ModelInferenceError("Model failed")
    
    monkeypatch.setattr("skill_analyzer.routes.extract_skills_from_text", failing_extract)
    
    client = TestClient(app)
    resp = client.post("/extract_skills_from_text", json={"text": "test"})
    assert resp.status_code == 500
    assert "failed to extract" in resp.json()["detail"].lower()


def test_post_pdf_extraction_error(monkeypatch):
    """Test error handling when PDF extraction fails."""
    async def failing_extract_pdf(file):
        raise PDFExtractionError("Failed to extract PDF")
    
    monkeypatch.setattr("skill_analyzer.routes.extract_text_from_pdf", failing_extract_pdf)
    
    client = TestClient(app)
    resp = client.post(
        "/extract_skills_from_pdf",
        files={"file": ("resume.pdf", b"data", "application/pdf")},
    )
    assert resp.status_code == 400
    assert "failed to extract text" in resp.json()["detail"].lower()


def test_post_text_database_error(monkeypatch):
    """Test graceful handling when database is unavailable."""
    async def failing_find(skills):
        raise DatabaseError("Database connection failed")
    
    monkeypatch.setattr("skill_analyzer.routes.find_courses", failing_find)
    monkeypatch.setattr("skill_analyzer.routes.extract_skills_from_text", lambda text: ["skill1", "skill2"])
    
    client = TestClient(app)
    resp = client.post("/extract_skills_from_text", json={"text": "test"})
    # Should still succeed but without courses
    assert resp.status_code == 200
    result = resp.json()
    assert len(result) == 2
    assert all(item["course"] is None for item in result)


def test_post_text_kafka_error(monkeypatch):
    """Test graceful handling when Kafka is unavailable."""
    class FailingProducer:
        async def send(self, topic, value):
            raise Exception("Kafka connection failed")
    
    class FailingKafkaManager:
        def __init__(self):
            self.producer = FailingProducer()
    
    monkeypatch.setattr("skill_analyzer.routes.kafka_manager", FailingKafkaManager())
    
    client = TestClient(app)
    resp = client.post("/extract_skills_from_text", json={"text": "test"})
    # Should still succeed even if Kafka fails
    assert resp.status_code == 200
