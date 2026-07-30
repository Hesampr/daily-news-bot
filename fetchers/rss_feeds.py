import re
import socket
import feedparser
import requests
from datetime import datetime, timedelta

# 구글뉴스/변환/뉴스레터 피드까지 한 번에 순회 (없으면 RSS_SOURCES로 폴백)
try:
    from config import ALL_FEEDS as FEEDS
except ImportError:
    from config import RSS_SOURCES as FEEDS

try:
    from config import source_region
except ImportError:
    def source_region(_name):
        return "global"

# 일부 피드(구글뉴스 등)는 기본 UA 차단/행 지연 → UA 지정 + 소켓 타임아웃
feedparser.USER_AGENT = "daily-news-bot/1.0 (+https://github.com/moong1755-ops/daily-news-bot)"
socket.setdefaulttimeout(15)


def fetch() -> tuple:
    articles = []
    errors = []
    yesterday = datetime.utcnow() - timedelta(days=1)

    for source_name, url in FEEDS.items():
        if not url or url.startswith("<"):   # 주석 자리표시자(미설정) 스킵
            continue
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; daily-news-bot/1.0)"
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                print(f"⚠️ RSS 파싱 경고 - {source_name}: {feed.bozo_exception}")

            for entry in feed.entries[:10]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                if not title or not link:
                    continue

                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < yesterday and source_name not in [
                        "McKinsey Insights",
                        "BCG Insights",
                        "PwC strategy+business",
                        "SSIR",
                        "PitchBook News",
                    ]:
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
                    "region": source_region(source_name),
                    "description": description,
                })
        except Exception as e:
            errors.append(f"{source_name} ({url}): {str(e)}")

    return articles, errors
