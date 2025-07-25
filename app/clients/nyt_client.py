import httpx
import ssl
import os
import certifi
import httpx
from fastapi import HTTPException
TOP_STORIES_BASE_URL = "https://api.nytimes.com/svc/topstories/v2"
ARTICLE_SEARCH_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
ssl_context = ssl.create_default_context(cafile=certifi.where())


async def fetch_top_stories(category: str) -> dict:
    valid_sections = os.getenv("NYT_VALID_SECTIONS", "").split(",")
    api_key = os.getenv("NYT_API_KEY") 
    if not api_key:
        raise RuntimeError("Missing NYT_API_KEY")

    if category not in valid_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{category}'. Must be one of: {', '.join(valid_sections)}"
        )

    params = {"api-key": api_key}
    url = f"https://api.nytimes.com/svc/topstories/v2/{category}.json"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(
                status_code=503,
                detail="Too many requests to NYT API. Please try again later."
            )
        elif exc.response.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category '{category}' — NYT API returned 404 Not Found."
            )
        else:
            print(f"HTTP Status error: {exc.response.status_code} - {exc.response.text}")
        raise
    except httpx.RequestError as e:
        print(f"HTTP Request failed: {e}")
        raise

async def fetch_article_search(q: str, begin_date=None, end_date=None):
    api_key = os.getenv("NYT_API_KEY") 
    if not api_key:
        raise RuntimeError("Missing NYT_API_KEY")
    params = {
        "q": q,
        "api-key": api_key,
    }
    if begin_date:
        params["begin_date"] = begin_date
    if end_date:
        params["end_date"] = end_date

    async with httpx.AsyncClient(verify=ssl_context) as client:
        response = await client.get(ARTICLE_SEARCH_URL, params=params)
        response.raise_for_status()
        return response.json()
