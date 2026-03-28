import pytest
from fastapi.testclient import TestClient
from job_service.main import app


@pytest.fixture(autouse=True)
def patch_job_service_deps(monkeypatch):
    # Избежим создания реального ThreadPool для unit-тестов
    from job_service.threadpool import threadpool_manager

    monkeypatch.setattr(threadpool_manager, "create", lambda: None)
    monkeypatch.setattr(threadpool_manager, "stop", lambda: None)

    # Заглушка для get_vacancy_by_id
    async def fake_get_vacancy_by_id(vacancy_id):
        class Vacancy:
            id = vacancy_id
            name = "Test vacancy"
            description = "Test description"
            employer = "Test employer"
            salary = "1000"
            employment = "Full-time"
            schedule = "Flexible"
            experience = "No experience"
            area = "Remote"

        return Vacancy()

    monkeypatch.setattr("job_service.routes.get_vacancy_by_id", fake_get_vacancy_by_id)

    # Заглушка для recommendations_sort
    async def fake_recommendations_sort(resume_text):
        class VacancyShort:
            id = 1
            name = "Test vacancy"
            employer = "Test employer"
            salary = "1000"
            area = "Remote"

        return [VacancyShort()]

    monkeypatch.setattr("job_service.routes.recommendations_sort", fake_recommendations_sort)

    # Заглушка для extract_text_from_pdf
    async def fake_extract_text_from_pdf(file):
        return "Пример текста резюме"

    monkeypatch.setattr("job_service.routes.extract_text_from_pdf", fake_extract_text_from_pdf)


def test_health_ok():
    client = TestClient(app)
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


def test_recommendations_from_text_success():
    client = TestClient(app)
    resp = client.post("/recommendations_from_text", json={"resume": "Мой опыт и навыки"})

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert resp.json()[0]["id"] == 1


def test_recommendations_from_text_empty_resume():
    client = TestClient(app)
    resp = client.post("/recommendations_from_text", json={"resume": ""})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Резюме не может быть пустым"


def test_recommendations_from_text_too_long():
    client = TestClient(app)
    long_resume = "a" * 50001
    resp = client.post("/recommendations_from_text", json={"resume": long_resume})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Резюме слишком длинное (максимум 50000 символов)"


def test_recommendations_from_pdf_bad_content_type():
    client = TestClient(app)
    resp = client.post(
        "/recommendations_from_pdf",
        files={"file": ("resume.txt", b"data", "text/plain")},
    )

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Допускается только PDF файлы"


def test_recommendations_from_pdf_success():
    client = TestClient(app)
    resp = client.post(
        "/recommendations_from_pdf",
        files={"file": ("resume.pdf", b"data", "application/pdf")},
    )

    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert resp.json()[0]["id"] == 1


def test_get_vacancy_found():
    client = TestClient(app)
    resp = client.get("/vacancies/42")

    assert resp.status_code == 200
    assert resp.json()["id"] == 42


def test_get_vacancy_not_found(monkeypatch):
    async def fake_none(vacancy_id):
        return None

    monkeypatch.setattr("job_service.routes.get_vacancy_by_id", fake_none)

    client = TestClient(app)
    resp = client.get("/vacancies/1000")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Вакансия не найдена"