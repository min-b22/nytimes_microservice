import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from unittest.mock import patch
from fastapi import HTTPException

import pytest_asyncio
from app.main import app

@pytest_asyncio.fixture
async def test_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_articlesearch_with_valid_query(test_client):
    response = await test_client.get("/nytimes/articlesearch", params={"q": "apple"})
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_articlesearch_invalid_date_format(test_client):
    response = await test_client.get("/nytimes/articlesearch", params={"begin_date": "abcd1301"})
    
    assert response.status_code == 422
    assert response.json()["detail"] == "Dates must be in YYYYMMDD format and valid calendar dates."

@pytest.mark.asyncio
async def test_articlesearch_begin_is_later_than_end(test_client):
    response = await test_client.get("/nytimes/articlesearch", params={"begin_date": "20250801", "end_date":"20250701"})
    
    assert response.status_code == 422
    assert response.json()["detail"] == "begin_date must be earlier than end_date."

@pytest.mark.asyncio
@patch("app.clients.nyt_client.fetch_article_search")
async def test_articlesearch_rate_limited(mock_fetch, test_client):
    mock_fetch.side_effect = HTTPException(
        status_code = 503,
        detail = "Too many requests to NYT API. Please try again later."
    )

    response = await test_client.get("/nytimes/articlesearch")

    assert response.status_code == 503
    assert response.json()["detail"] == "Too many requests to NYT API. Please try again later."

@pytest.mark.asyncio
@patch("app.clients.nyt_client.fetch_article_search")
async def test_articlesearch_internal_server_error(mock_fetch, test_client, capfd):
    mock_fetch.side_effect = RuntimeError("Some error")

    response = await test_client.get("/nytimes/articlesearch?q=climate")

    assert response.status_code == 500
    assert response.json()["detail"] == "Unexpected error occurred during article search."
    captured = capfd.readouterr()
    assert "Unexpected error during article search: Some error" in captured.out
