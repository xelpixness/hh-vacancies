import requests
import json
from ..models import Vacancy
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

    def fetch_page(self, page: int) -> List[dict]:
        params = {"text": self.search_words, "per_page": self.per_page, "page": page}
        try:
            r = requests.get(
                self.BASE_URL, headers=self.headers, params=params, timeout=10
            )
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"Request failed on page {page}: {e}")
            return []

        data = r.json()
        items = [Vacancy.from_api(v).model_dump() for v in data.get("items", [])]
        return items

    def fetch_all(self) -> List[dict]:
        self.vacancies = []

        first_page = self.fetch_page(0)
        self.vacancies.extend(first_page)

        if not first_page:
            return self.vacancies

        total_pages_hh, total_found_hh = self._get_search_metadata()
        print(f"Total pages: {total_pages_hh}, total vacancies found: {total_found_hh}")

        total_pages = min(total_pages_hh, self.max_pages)

        print(
            f"Fetching {total_pages} pages, found {len(self.vacancies)} vacancies on page 1"
        )

        for page in range(1, total_pages):
            page_items = self.fetch_page(page)
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

    def _get_search_metadata(self) -> tuple[int, int]:
        params = {"text": self.search_words, "per_page": self.per_page, "page": 0}
        try:
            r = requests.get(
                self.BASE_URL, headers=self.headers, params=params, timeout=10
            )
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to get total pages: {e}")
            return 0, 0

        response_dict = r.json()
        total_pages = response_dict.get("pages", 0)
        total_found = response_dict.get("found", 0)

        return total_pages, total_found


# --------------------------
# CLI launch
# --------------------------
if __name__ == "__main__":
    search_words = input("Enter search keywords: ")
    parser = HHParser(search_words=search_words, per_page=100, max_pages=20)
    parser.fetch_all()
    parser.save_json("vacancies.json")
