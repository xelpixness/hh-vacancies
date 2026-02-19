import time
from typing import List

# --------------------------
# cache
# --------------------------
CACHE_TTL = 300
cache: dict[str, dict] = {}


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
    vacancies: List[dict], remote: bool | None, experience_list: list[str] | None
) -> List[dict]:
    return [
        v
        for v in vacancies
        if filter_remote(v, remote) and filter_experience(v, experience_list)
    ]
