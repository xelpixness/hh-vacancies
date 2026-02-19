from fastapi import FastAPI, Query
import uvicorn
import json
from models import VacanciesResponse
from typing import Literal

app = FastAPI()


# --------------------------
# filters
# --------------------------
def map_experience(exp_str: str | None) -> str | None:
    if not exp_str:
        return None
    exp_str = exp_str.lower()
    if "нет опыта" in exp_str:
        return "no_experience"
    if "от 1 года до 3 лет" in exp_str:
        return "1_3"
    if "от 3 до 6 лет" in exp_str:
        return "3_6"
    if "более 6 лет" in exp_str:
        return "6_plus"
    return None


def filter_remote(vacancy: dict, remote: bool | None) -> bool:
    if remote is None:
        return True
    work_format = vacancy.get("work_format") or []
    return any(wf.lower() == "удалённо" for wf in work_format) if remote else True


def filter_experience(vacancy: dict, experience_list: list[str] | None) -> bool:
    if not experience_list:
        return True
    vacancy_exp = map_experience(vacancy.get("experience"))
    return vacancy_exp in experience_list


def apply_filters(
    vacancies: list[dict], remote: bool | None, experience_list: list[str] | None
) -> list[dict]:
    return [
        v
        for v in vacancies
        if filter_remote(v, remote) and filter_experience(v, experience_list)
    ]


# --------------------------
# endpoints
# --------------------------
@app.get("/api/vacancies")
def get_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    remote: bool | None = Query(None),
    experience: list[Literal["no_experience", "1_3", "3_6", "6_plus"]] | None = Query(
        None, description="Categories: no_experience, 1_3, 3_6, 6_plus"
    ),
) -> VacanciesResponse:
    with open("vacancies.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    data = apply_filters(data, remote=remote, experience_list=experience)

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
