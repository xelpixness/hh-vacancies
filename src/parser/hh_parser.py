import requests
import json
from src.models import VacancySchema
from typing import List, Optional


class HHParser:
    BASE_URL = "https://api.hh.ru/vacancies"
    MAX_PAGES_LIMIT = 100
    PER_PAGE_LIMIT = 100

    def __init__(
        self, search_words: str, per_page: int = 100, max_pages: Optional[int] = None
    ):
        self.search_words = search_words
        self.per_page = min(per_page, self.PER_PAGE_LIMIT)
        if max_pages is None:
            self.max_pages = self.MAX_PAGES_LIMIT
        else:
            self.max_pages = min(max_pages, self.MAX_PAGES_LIMIT)
        self.headers = {"User-Agent": "hh-vacancies/0.1 (pet-project)"}
        self.vacancies: List[dict] = []

    def fetch_page(self, page: int) -> tuple[List[dict], int, int]:
        params = {"text": self.search_words, "per_page": self.per_page, "page": page}
        try:
            r = requests.get(
                self.BASE_URL, headers=self.headers, params=params, timeout=10
            )
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"Request failed on page {page}: {e}")
            return [], 0, 0

        data = r.json()
        items = [VacancySchema.from_api(v).model_dump() for v in data.get("items", [])]
        total_pages = data.get("pages", 0)
        total_found = data.get("found", 0)

        return items, total_pages, total_found

    def fetch_all(self) -> List[dict]:
        self.vacancies = []

        first_page, total_pages_hh, total_found_hh = self.fetch_page(0)
        self.vacancies.extend(first_page)

        if not first_page:
            return self.vacancies

        print(f"Total pages: {total_pages_hh}, total vacancies found: {total_found_hh}")

        total_pages = min(total_pages_hh, self.max_pages)

        print(
            f"Fetching {total_pages} pages, found {len(self.vacancies)} vacancies on page 1"
        )

        for page in range(1, total_pages):
            page_items, _, _ = self.fetch_page(page)
            if not page_items:
                continue
            self.vacancies.extend(page_items)
            print(f"Fetched page {page+1}, total vacancies: {len(self.vacancies)}")

        return self.vacancies

    def save_json(self, filename: str):
        if not self.vacancies:
            print("No vacancies to save.")
            return
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.vacancies, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.vacancies)} vacancies to {filename}")


# --------------------------
# CLI launch
# --------------------------
if __name__ == "__main__":
    search_words = input("Enter search keywords: ")
    parser = HHParser(search_words=search_words, per_page=100, max_pages=20)
    parser.fetch_all()
    parser.save_json("vacancies.json")
