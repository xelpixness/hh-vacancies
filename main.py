import requests

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
    vacancy_dict = vacancies_dict[0]

    print("\n🔮 Selected information about first vacancy:\n")

    print(f"Vacancy URL: {vacancy_dict['alternate_url']}")
    print(f"API URL: {vacancy_dict['employer']['vacancies_url']}")

    print(f"Name: {vacancy_dict['name']}")
    print(f"Company: {vacancy_dict['employer']['name']}")
    print(f"Experience: {vacancy_dict['experience']['name']}")
    print("Work Formats:")
    for i, format in enumerate(vacancy_dict["work_format"], 1):
        print(f"\t{i}. {format['name']}")
except IndexError:
    pass
