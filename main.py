import requests
import json
from models import Vacancy

search_words = input("Enter search keywords: ")
url = "https://api.hh.ru/vacancies"
headers = {"User-Agent": "hh-vacancies/0.1 (pet-project)"}
per_page = 100

all_vacancies = []
params = {"text": search_words, "per_page": per_page, "page": 0}

try:
    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()
except requests.RequestException as e:
    print("API request failed:", e)
    exit(1)

response_dict = r.json()
total_pages = response_dict.get("pages", 0)
print(
    f"Total pages: {total_pages}, total vacancies found: {response_dict.get('found')}"
)

for vac_dict in response_dict.get("items", []):
    all_vacancies.append(Vacancy.from_api(vac_dict).model_dump())

for page in range(1, total_pages):
    params["page"] = page
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed on page {page}: {e}")
        continue

    response_dict = r.json()
    for vac_dict in response_dict.get("items", []):
        all_vacancies.append(Vacancy.from_api(vac_dict).model_dump())

with open("vacancies.json", "w", encoding="utf-8") as f:
    json.dump(all_vacancies, f, ensure_ascii=False, indent=2)

print(f"Saved {len(all_vacancies)} vacancies to vacancies.json")
