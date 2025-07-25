from pydantic import BaseModel

class TopStory(BaseModel):
    title: str
    section: str
    url: str
    abstract: str
    published_date: str

class ArticleSearchResult(BaseModel):
    headline: str
    snippet: str
    web_url: str
    pub_date: str
