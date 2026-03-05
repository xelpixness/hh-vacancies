from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import app
from src.models import VacancySchema

client = TestClient(app)

MOCK_VACANCY = VacancySchema(
    id="1",
    name="Python Developer",
    area_name="Москва",
    experience="От 1 года до 3 лет",
    work_format=["Удалённо"],
    published_at="2026-01-01T10:00:00+0300",
)


def test_get_vacancies_no_query():
    response = client.get("/api/vacancies")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@patch("src.main.redis_client.get", new_callable=AsyncMock, return_value=None)
@patch("src.main.redis_client.set", new_callable=AsyncMock)
@patch(
    "src.main.HHParser.fetch_all", new_callable=AsyncMock, return_value=[MOCK_VACANCY]
)
def test_get_vacancies_with_query(mock_fetch, mock_set, mock_get):
    response = client.get("/api/vacancies?query=python")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Python Developer"


@patch("src.main.redis_client.get", new_callable=AsyncMock, return_value=None)
@patch("src.main.redis_client.set", new_callable=AsyncMock)
@patch(
    "src.main.HHParser.fetch_all", new_callable=AsyncMock, return_value=[MOCK_VACANCY]
)
def test_filter_remote_only(mock_fetch, mock_set, mock_get):
    response = client.get("/api/vacancies?query=python&remote=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@patch("src.main.redis_client.get", new_callable=AsyncMock, return_value=None)
@patch("src.main.redis_client.set", new_callable=AsyncMock)
@patch(
    "src.main.HHParser.fetch_all", new_callable=AsyncMock, return_value=[MOCK_VACANCY]
)
def test_filter_remote_excludes_non_remote(mock_fetch, mock_set, mock_get):
    vacancy_office = VacancySchema(id="2", name="Office Job", work_format=["В офисе"])
    mock_fetch.return_value = [MOCK_VACANCY, vacancy_office]
    response = client.get("/api/vacancies?query=python&remote=true")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Python Developer"


@patch("src.main.redis_client.get", new_callable=AsyncMock, return_value=None)
@patch("src.main.redis_client.set", new_callable=AsyncMock)
@patch("src.main.HHParser.fetch_all", new_callable=AsyncMock)
def test_pagination(mock_fetch, mock_set, mock_get):
    mock_fetch.return_value = [
        VacancySchema(id=str(i), name=f"Vacancy {i}") for i in range(25)
    ]
    response = client.get("/api/vacancies?query=python&page=2&per_page=10")
    data = response.json()
    assert data["total"] == 25
    assert len(data["items"]) == 10
    assert data["page"] == 2
