import os
from typing import List, Optional
from fastapi import HTTPException
from app.clients import nyt_client
from app.models.nyt_models import TopStory, ArticleSearchResult
import httpx

RETRY_DELAY = 12

async def get_combined_top_stories():
    categories = os.getenv("NYT_CATEGORIES", "").split(",")
    if not categories:
        print(f"No categories defined in NYT_CATEGORIES")
        raise RuntimeError("Missing NYT_CATEGORIES")
    results = []

    for category in categories:
        try:
            data = await nyt_client.fetch_top_stories(category)
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            if status_code == 404:
                print(f"Invalid category '{category}': 404 Not Found")
                raise  # stop everything
            else:
                print(f"HTTP error for '{category}': {status_code}")
                continue

        filtered = [
            item for item in data.get("results", [])
            if item.get("url", "").startswith("https://www.nytimes.com")
            and all(item.get(k) not in [None, ""] for k in ["title", "abstract", "published_date", "section"])
        ]#skip non-article data

        for item in filtered[:2]:
            results.append(TopStory(
                title=item["title"],
                section=item["section"],
                url=item["url"],
                abstract=item["abstract"],
                published_date=item["published_date"]
            ))

    if not results:
        raise RuntimeError("No valid stories found.")
    print(f"✅ Total results collected: {len(results)}")
    return results


async def search_articles(
    q: str = None,
    begin_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[ArticleSearchResult]:
    try:
        data = await nyt_client.fetch_article_search(q, begin_date, end_date)
        docs = data.get("response", {}).get("docs", [])
        results = []

        for doc in docs:
            headline = doc.get("headline", {}).get("main")
            snippet = doc.get("snippet")
            web_url = doc.get("web_url")
            pub_date = doc.get("pub_date")

            if not all([headline, snippet, web_url, pub_date]):
                continue  # skip non-article data

            results.append(ArticleSearchResult(
                headline=headline,
                snippet=snippet,
                web_url=web_url,
                pub_date=pub_date
            ))

        return results

    except Exception as e:
        print(f"Error during article search: {e}")
        return []
