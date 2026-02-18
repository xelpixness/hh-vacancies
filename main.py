import requests
from pprint import pprint
from models import Vacancy

# 'GET https://api.hh.ru/vacancies?text=python&per_page=100&page=0'

search_words = input()
# search_words = "flask javascript"

url = f"https://api.hh.ru/vacancies?text={search_words}"
url += "&per_page=100&page=0"

headers = {"User-Agent": "hh-vacancies/0.1 (pet-project)"}

r = requests.get(url, headers=headers)

response_dict = r.json()

print(f"Total vacancies: {response_dict['found']}")

vacancies_dict = response_dict["items"]

try:
    vacancy_dict = vacancies_dict[1]
    vac = Vacancy.from_api(vacancy_dict)
    pprint(vac.model_dump())

except IndexError:
    pass
