from pydantic import BaseModel, Field


class SalarySchema(BaseModel):
    from_: float | None = Field(default=None, alias="from")
    to: float | None = None
    currency: str | None = None
    gross: bool | None = None


class VacancySchema(BaseModel):
    id: str
    name: str | None = None
    published_at: str | None = None
    url: str | None = None

    area_name: str | None = None

    employer_name: str | None = None
    employer_url: str | None = None

    employment: str | None = None
    experience: str | None = None
    schedule: str | None = None

    work_format: list[str] = Field(default_factory=list)

    salary: SalarySchema | None = None

    requirement: str | None = None
    responsibility: str | None = None

    @classmethod
    def from_api(cls, v: dict):
        salary_raw = v.get("salary")
        salary = (
            SalarySchema(
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


class VacanciesResponseSchema(BaseModel):
    items: list[VacancySchema]
    total: int
    page: int
    per_page: int
