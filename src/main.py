from fastapi import FastAPI, Query
import uvicorn
import time
import json
from src.models import VacanciesResponseSchema, VacancySchema
from typing import Literal
from contextlib import asynccontextmanager

from src.parser.hh_parser import HHParser
from src.utils import apply_filters, sort_vacancies
from src.redis_client import redis_client
from src.config import settings
from fastapi.responses import FileResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.aclose()


app = FastAPI(lifespan=lifespan)


def build_cache_key(query: str | None) -> str:
    return f"vacancies:{query or 'all'}"


# --------------------------
# endpoints
# --------------------------
@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/api/vacancies")
async def get_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    remote: bool | None = Query(None),
    experience: list[Literal["no_experience", "1_3", "3_6", "6_plus"]] | None = Query(
        None, description="Categories: no_experience, 1_3, 3_6, 6_plus"
    ),
    query: str | None = Query(None, description="Search keywords for HH API"),
    city: str | None = Query(None, description="Filter by area"),
    sort: Literal["asc", "desc"] = Query("desc", description="Sort by published_at"),
) -> VacanciesResponseSchema:

    data: list = []

    if query:
        key = build_cache_key(query)
        cached = await redis_client.get(key)
        if cached:
            data = [VacancySchema.model_validate(v) for v in json.loads(cached)]
        else:
            parser = HHParser(search_words=query)
            data = await parser.fetch_all()
            await redis_client.set(
                key, json.dumps([v.model_dump() for v in data]), ex=settings.CACHE_TTL
            )

    data = apply_filters(data, remote=remote, experience_list=experience, city=city)
    reverse = sort == "desc"
    data = sort_vacancies(data, by="published_at", reverse=reverse)

    total = len(data)
    start = (page - 1) * per_page
    end = start + per_page
    items = data[start:end]

    return VacanciesResponseSchema(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
    )


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
