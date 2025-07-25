from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.models.nyt_models import TopStory, ArticleSearchResult
from app.services import nyt_service
from datetime import datetime

router = APIRouter()

def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Dates must be in YYYYMMDD format and valid calendar dates."
        )

def validate_date_format_and_order(begin_date: Optional[str], end_date: Optional[str]):
    begin = parse_date(begin_date) if begin_date else None
    end = parse_date(end_date) if end_date else None

    if begin and end and begin >= end:
        raise HTTPException(
            status_code=422,
            detail="begin_date must be earlier than end_date."
        )

@router.get(
    "/topstories",
    response_model=List[TopStory],
    responses={
        503: {"description": "NYT API rate limit exceeded"},
        400: {"description": "Invalid category"},
        500: {"description": "No valid stories found"}
    }
)
async def get_top_stories():
    return await nyt_service.get_combined_top_stories()

@router.get(
    "/articlesearch",
    response_model=List[ArticleSearchResult],
    responses={
        422: {"description": "Invalid date format or range"},
        400: {"description": "Bad request"},
        503: {"description": "NYT API rate limit exceeded"},
    }
)
async def search_articles(
    q: str = Query(None, description="Keyword"),
    begin_date: Optional[str] = Query(None, description="YYYYMMDD"),
    end_date: Optional[str] = Query(None, description="YYYYMMDD")
):
    if begin_date or end_date:
        validate_date_format_and_order(begin_date, end_date)

    return await nyt_service.search_articles(q, begin_date, end_date)
