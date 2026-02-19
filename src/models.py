from typing import List, Optional
from pydantic import BaseModel, Field


class Salary(BaseModel):
    from_: Optional[float] = Field(default=None, alias="from")
    to: Optional[float] = None
    currency: Optional[str] = None
    gross: Optional[bool] = None


class Vacancy(BaseModel):
    id: str
    name: Optional[str] = None
    published_at: Optional[str] = None
    url: Optional[str] = None

    area_name: Optional[str] = None

    employer_name: Optional[str] = None
    employer_url: Optional[str] = None

    employment: Optional[str] = None
    experience: Optional[str] = None
    schedule: Optional[str] = None

    work_format: List[str] = Field(default_factory=list)

    salary: Optional[Salary] = None

    requirement: Optional[str] = None
    responsibility: Optional[str] = None

    @classmethod
    def from_api(cls, v: dict):
        # salary
        salary_raw = v.get("salary")
        salary = (
            Salary(
                from_=salary_raw.get("from") if salary_raw else None,
                to=salary_raw.get("to") if salary_raw else None,
                currency=salary_raw.get("currency") if salary_raw else None,
                gross=salary_raw.get("gross") if salary_raw else None,
            )
            if salary_raw
            else None
        )

        work_format_raw = v.get("work_format") or []
        work_format = [wf.get("name") for wf in work_format_raw if wf.get("name")]

        return cls(
            id=v.get("id"),
            name=v.get("name"),
            published_at=v.get("published_at"),
            url=v.get("alternate_url"),
            area_name=(v.get("area") or {}).get("name"),
            employer_name=(v.get("employer") or {}).get("name"),
            employer_url=(v.get("employer") or {}).get("alternate_url"),
            employment=(v.get("employment") or {}).get("name"),
            experience=(v.get("experience") or {}).get("name"),
            schedule=(v.get("schedule") or {}).get("name"),
            work_format=work_format,
            salary=salary,
            requirement=(v.get("snippet") or {}).get("requirement"),
            responsibility=(v.get("snippet") or {}).get("responsibility"),
        )


class VacanciesResponse(BaseModel):
    items: List[Vacancy]
    total: int
    page: int
    per_page: int
