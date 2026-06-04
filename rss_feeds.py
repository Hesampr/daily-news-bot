import re
import feedparser
from datetime import datetime, timedelta

from config import RSS_SOURCES


def fetch() -> tuple:
    articles = []
    errors = []
    yesterday = datetime.utcnow() - timedelta(days=1)

    for source_name, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)

            if feed.bozo and not feed.entries:
                raise Exception(f"Failed to parse feed: {feed.bozo_exception}")

            for entry in feed.entries[:10]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()

                if not title or not link:
                    continue

                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < yesterday:
                        continue
                    date_str = pub_date.strftime("%Y-%m-%d")
                else:
                    date_str = "Unknown date"

                description = entry.get("summary") or entry.get("description") or ""
                description = re.sub(r"<[^>]+>", "", description).strip()[:500]

                articles.append({
                    "title": title,
                    "link": link,
                    "date": date_str,
                    "source": source_name,
                    "description": description,
                })

        except Exception as e:
            errors.append(f"{source_name}: {str(e)}")

    return articles, errors
