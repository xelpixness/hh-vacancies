from src.utils import map_experience, filter_remote, filter_experience, filter_city
from src.models import VacancySchema


def make_vacancy(**kwargs) -> VacancySchema:
    defaults = {"id": "1", "name": "Test vacancy"}
    return VacancySchema(**{**defaults, **kwargs})


def test_map_experience_no_experience():
    assert map_experience("Нет опыта") == "no_experience"


def test_map_experience_unknown_returns_none():
    assert map_experience("что-то странное") is None


def test_filter_remote_true():
    v = make_vacancy(work_format=["Удалённо"])
    assert filter_remote(v, remote=True) is True


def test_filter_remote_false_when_no_remote():
    v = make_vacancy(work_format=["В офисе"])
    assert filter_remote(v, remote=True) is False


def test_filter_city_match():
    v = make_vacancy(area_name="Москва")
    assert filter_city(v, city="Москва") is True


def test_filter_city_no_match():
    v = make_vacancy(area_name="Москва")
    assert filter_city(v, city="Казань") is False


def test_filter_experience_match():
    v = make_vacancy(experience="От 1 года до 3 лет")
    assert filter_experience(v, experience_list=["1_3"]) is True


def test_filter_experience_no_match():
    v = make_vacancy(experience="От 1 года до 3 лет")
    assert filter_experience(v, experience_list=["3_6"]) is False


def test_filter_experience_none_returns_all():
    v = make_vacancy(experience="От 1 года до 3 лет")
    assert filter_experience(v, experience_list=None) is True
