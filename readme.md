# NYTimes Article Microservice

This microservice provides endpoints to access and search for articles using the New York Times API.

## Endpoints

---

### GET `/nytimes/topstories`

Fetches the top 2 latest stories from each of the pre-configured NYT sections.
- `arts`
- `food`
- `movies`
- `travel`
- `science`

#### Query Parameters

_None_

#### Response

Returns a list of articles. Each item contains:

```json
[
  {
    "title": "Article title",
    "abstract": "Short summary",
    "url": "https://www.nytimes.com/...",
    "published_date": "2024-06-12T12:00:00Z",
    "section": "arts"
  },
  ...
]
```

Only results with all fields and a valid URL (`https://www.nytimes.com/...`) are returned.

#### Error Responses

- `400 Bad Request`: Invalid category from environment
- `503 Service Unavailable`: Rate limit exceeded on NYT API
- `500 Internal Server Error`: Unexpected failure

---

### GET `/nytimes/articlesearch`

Searches for articles using the NYT Article Search API.

#### Query Parameters

| Name         | Type   | Required | Description                                       |
|--------------|--------|----------|---------------------------------------------------|
| `q`          | string | No       | Keyword or search term                            |
| `begin_date` | string | No       | Start date in `YYYYMMDD` format                   |
| `end_date`   | string | No       | End date in `YYYYMMDD` format (exclusive)         |

- `begin_date` must be earlier than `end_date`.
- Dates must be valid calendar dates in `YYYYMMDD` format.

#### Response

Returns a list of matching articles. Each item contains:

```json
[
  {
    "headline": "Title of the article",
    "snippet": "Short summary of the article",
    "web_url": "https://www.nytimes.com/...",
    "pub_date": "2024-06-12T14:20:00+0000"
  },
  ...
]
```

Only articles with all four fields present are included.

#### Error Responses

- `422 Unprocessable Entity`: Invalid date format or date order
- `503 Service Unavailable`: Rate limit exceeded on NYT API
- `500 Internal Server Error`: Unexpected failure

---

## Environment Variables

| Variable            | Description                            |
|---------------------|----------------------------------------|
| `NYT_API_KEY`       | Your NYT API key                       |
| `NYT_CATEGORIES`    | Comma-separated list of sections (e.g. `arts,science,...`) |
| `NYT_VALID_SECTIONS`| Comma-separated list of all valid NYT sections (for validation) |

---

## Notes

- Rate limits: 5 requests/minute, 500/day for Top Stories API. (https://developer.nytimes.com/faq#a11)
