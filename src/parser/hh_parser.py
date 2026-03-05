# import requests
import asyncio
import httpx

import json
from src.models import VacancySchema


class HHParser:
    BASE_URL = "https://api.hh.ru/vacancies"
    MAX_PAGES_LIMIT = 100
    PER_PAGE_LIMIT = 100

    def __init__(
        self,
        search_words: str,
        per_page: int = 100,
        max_pages: int | None = None,
        max_concurrent: int = 5,
    ):
        self.search_words = search_words
        self.per_page = min(per_page, self.PER_PAGE_LIMIT)
        self.max_pages = min(
            max_pages if max_pages is not None else 15, self.MAX_PAGES_LIMIT
        )
        self.headers = {"User-Agent": "hh-vacancies/0.1 (pet-project)"}
        self.vacancies: list[VacancySchema] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_page(
        self, client: httpx.AsyncClient, page: int
    ) -> tuple[list[VacancySchema], int, int]:
        async with self.semaphore:
            params = {
                "text": self.search_words,
                "per_page": self.per_page,
                "page": page,
            }
            try:
                r = await client.get(
                    self.BASE_URL, headers=self.headers, params=params, timeout=10
                )
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error on page {page}: {e.response.status_code}")
                return [], 0, 0
            except httpx.RequestError as e:
                print(f"Request failed on page {page}: {e}")
                return [], 0, 0

            data = r.json()
            items = [VacancySchema.from_api(v) for v in data.get("items", [])]
            total_pages = data.get("pages", 0)
            total_found = data.get("found", 0)
            return items, total_pages, total_found

    async def fetch_all(self) -> list[VacancySchema]:
        self.vacancies = []

        async with httpx.AsyncClient() as client:
            first_page, total_pages_hh, total_found_hh = await self.fetch_page(
                client, 0
            )
            self.vacancies.extend(first_page)

            if not first_page:
                return self.vacancies

            total_pages = min(total_pages_hh, self.max_pages)
            print(
                f"Total pages: {total_pages_hh}, total vacancies found: {total_found_hh}"
            )
            print(
                f"Fetching {total_pages} pages, found {len(self.vacancies)} vacancies on page 1"
            )

            tasks = [self.fetch_page(client, page) for page in range(1, total_pages)]
            results = await asyncio.gather(*tasks)
            for page_items, _, _ in results:
                if page_items:
                    self.vacancies.extend(page_items)
                    print(
                        f"Fetched {len(page_items)} vacancies, total so far: {len(self.vacancies)}"
                    )

        return self.vacancies

    def save_json(self, filename: str):
        if not self.vacancies:
            print("No vacancies to save.")
            return
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                [v.model_dump() for v in self.vacancies],
                f,
                ensure_ascii=False,
                indent=2,
            )
            # json.dump(self.vacancies, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.vacancies)} vacancies to {filename}")


# --------------------------
# CLI launch
# --------------------------
if __name__ == "__main__":
    search_words = input("Enter search keywords: ")
    parser = HHParser(search_words=search_words, per_page=100, max_pages=20)
    vacancies = asyncio.run(parser.fetch_all())
    parser.vacancies = vacancies
    parser.save_json("vacancies.json")
