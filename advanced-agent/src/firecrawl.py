import os
from firecrawl import Firecrawl
from dotenv import load_dotenv

load_dotenv()


class FirecrawlService:
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("Missing FIRECRAWL_API_KEY environment variable")
        self.app = Firecrawl(api_key=api_key)

    def search_web(self, query: str, num_results: int = 5):
        """Plain search: best for finding URLs/titles."""
        try:
            return self.app.search(
                query=query,
                limit=num_results,
            )
        except Exception as e:
            print(f"Search error: {e}")
            return None

    def search_with_content(self, query: str, num_results: int = 5):
        """Search + scrape content from results."""
        try:
            return self.app.search(
                query=query,
                limit=num_results,
                scrape_options={"formats": ["markdown"]},
            )
        except Exception as e:
            print(f"Search+content error: {e}")
            return None

    def scrape_company_pages(self, url: str):
        try:
            if not url:
                return None
            return self.app.scrape(
                url,
                formats=["markdown"],
            )
        except Exception as e:
            print(f"Scrape error for {url}: {e}")
            return None