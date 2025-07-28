import os
import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from fastapi import status, HTTPException
from app.clients.nyt_client import get_api_key
from app.main import app
import pytest_asyncio

@pytest_asyncio.fixture
async def test_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@patch.dict(os.environ, {}, clear=True)
def test_get_api_key_missing():
    with pytest.raises(RuntimeError, match="Missing NYT_API_KEY"):
        get_api_key()

@pytest.mark.asyncio
@patch("app.clients.nyt_client.fetch_top_stories")
async def test_get_topstories_success(mock_fetch, test_client):
    mock_data = {
        "results": [
            {
                "title": "Title A",
                "abstract": "Abstract A",
                "url": "https://www.nytimes.com/article-A",
                "published_date": "2024-06-01",
                "section": "arts"
            },
            {
                "title": "Title B",
                "abstract": "Abstract B",
                "url": "https://www.nytimes.com/article-B",
                "published_date": "2024-06-02",
                "section": "technology"
            }
        ]
    }

    mock_fetch.return_value = mock_data
    response = await test_client.get("/nytimes/topstories")
    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert isinstance(results, list)
    assert results[0]["title"] == "Title A"

@pytest.mark.asyncio
@patch("app.clients.nyt_client.fetch_top_stories")
async def test_get_topstories_rate_limited(mock_fetch, test_client):
    mock_fetch.side_effect = HTTPException(
        status_code=503,
        detail="Too many requests to NYT API. Please try again later."
    )
    response = await test_client.get("/nytimes/topstories")
    assert response.status_code == 503
    assert response.json()["detail"] == "Too many requests to NYT API. Please try again later."

@pytest.mark.asyncio
@patch("app.clients.nyt_client.fetch_top_stories")
async def test_get_topstories_invalid_category(mock_fetch, test_client):
    mock_fetch.side_effect = HTTPException(
        status_code=400,
        detail="Invalid category 'unknown'. Must be one of: arts, science, movies"
    )

    response = await test_client.get("/nytimes/topstories")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid category 'unknown'. Must be one of: arts, science, movies"

@pytest.mark.asyncio
@patch("app.clients.nyt_client.fetch_top_stories")
async def test_get_topstories_no_valid_articles(mock_fetch, test_client):
    mock_fetch.return_value = {"results": []}

    response = await test_client.get("/nytimes/topstories")

    assert response.status_code == 500
    assert response.json()["detail"] == "No valid stories found."
