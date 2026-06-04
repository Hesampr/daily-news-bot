import time
import requests
from datetime import datetime, timedelta


def fetch(keywords: list) -> tuple:
    articles = []
    errors = []
    yesterday = int((datetime.utcnow() - timedelta(days=1)).timestamp())

    for keyword in keywords[:4]:
        try:
            url = (
                f"https://hn.algolia.com/api/v1/search"
                f"?query={keyword}&tags=story"
                f"&numericFilters=created_at_i>{yesterday}"
                f"&hitsPerPage=5"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            for hit in data.get("hits", []):
                title = hit.get("title", "").strip()
                link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                date = hit.get("created_at", "")[:10]

                if not title or not link:
                    continue

                articles.append({
                    "title": title,
                    "link": link,
                    "date": date,
                    "source": "Hacker News",
                    "description": (hit.get("story_text") or "")[:500],
                })

            time.sleep(0.5)

        except Exception as e:
            errors.append(f"Hacker News (keyword: {keyword}): {str(e)}")

    return articles, errors
