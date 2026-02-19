from fastapi import FastAPI, Query
import uvicorn
import json
from models import VacanciesResponse

app = FastAPI()


@app.get("/api/vacancies")
def get_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> VacanciesResponse:
    with open("vacancies.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    total = len(data)
    start = (page - 1) * per_page
    end = start + per_page
    items = data[start:end]

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
