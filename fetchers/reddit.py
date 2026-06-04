import requests
from datetime import datetime, timedelta

from config import REDDIT_SUBREDDITS

HEADERS = {"User-Agent": "news-bot/1.0 (educational project)"}


def fetch() -> tuple:
    articles = []
    errors = []
    yesterday = datetime.utcnow() - timedelta(days=1)

    for subreddit in REDDIT_SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"
            response = requests.get(url, headers=HEADERS, timeout=10)
            print(f"Reddit r/{subreddit} status: {response.status_code}", flush=True)
            response.raise_for_status()
            data = response.json()

            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})

                title = post_data.get("title", "").strip()
                link = post_data.get("url", "").strip()
                created = post_data.get("created_utc", 0)

                if not title or not link:
                    continue

                pub_date = datetime.utcfromtimestamp(created)
                if pub_date < yesterday:
                    continue

                # Use permalink for text posts
                if "reddit.com" in link:
                    link = f"https://reddit.com{post_data.get('permalink', '')}"

                description = (post_data.get("selftext") or "")[:500]

                articles.append({
                    "title": title,
                    "link": link,
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "source": f"Reddit r/{subreddit}",
                    "description": description,
                })

        except Exception as e:
            print(f"Reddit r/{subreddit} error: {str(e)}", flush=True)
            errors.append(f"Reddit r/{subreddit}: {str(e)}")

    return articles, errors
