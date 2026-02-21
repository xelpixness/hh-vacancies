from fastapi import FastAPI, Query
import uvicorn
import time
from src.models import VacanciesResponseSchema, VacancySchema
from typing import Literal

from src.parser.hh_parser import HHParser
from src.utils import apply_filters, cache, CACHE_TTL, sort_vacancies

app = FastAPI()


# --------------------------
# endpoints
# --------------------------
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

    if query:
        now = time.time()
        cached = cache.get(query)
        if cached and (now - cached["timestamp"]) < CACHE_TTL:
            data = cached["data"]
        else:
            parser = HHParser(search_words=query)
            data = await parser.fetch_all()
            cache[query] = {"data": data, "timestamp": now}
    else:
        data = []

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
