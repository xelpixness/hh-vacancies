# hh-vacancies

A pet project for searching and filtering vacancies from the HH.ru API.

Built with FastAPI, Redis, and a minimal single-file frontend.

## Features

- Keyword-based vacancy search via HH.ru API
- Filters: remote work, city, experience level
- Result caching in Redis
- Dark / light theme toggle

## Stack

- Python 3.10, FastAPI, uvicorn
- Redis (async via redis-py)
- httpx for async HTTP requests
- Pydantic v2 for data validation
- Docker + docker-compose

## Running locally

**Requirements:** Python 3.10+, Poetry, Redis

```bash
git clone https://github.com/your-username/hh-vacancies.git
cd hh-vacancies

poetry install
cp .env.example .env

uvicorn src.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000)

## Running with Docker

```bash
cp .env.example .env
docker-compose up --build
```

Open [http://localhost:8000](http://localhost:8000)

## Running tests

```bash
poetry run pytest -v
```

## Project structure

```
.
├── src/
│   ├── main.py          # FastAPI app and endpoints
│   ├── models.py        # Pydantic schemas
│   ├── utils.py         # Filters and sorting
│   ├── config.py        # Settings
│   ├── redis_client.py  # Redis connection
│   └── parser/
│       └── hh_parser.py # HH.ru API client
├── static/
│   └── index.html       # Frontend
├── tests/
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

test github actions
test github actions again