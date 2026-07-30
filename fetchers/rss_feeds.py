import re
import socket
import feedparser
import requests
from datetime import datetime, timedelta

try:
    from config import ALL_FEEDS as FEEDS
except ImportError:
    from config import RSS_SOURCES as FEEDS

try:
    from config import source_region
except ImportError:
    def source_region(_name):
        return "global"


feedparser.USER_AGENT = (
    "daily-news-bot/1.0 "
    "(+https://github.com/moong1755-ops/daily-news-bot)"
)

socket.setdefaulttimeout(15)


def clean_html(text):
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    return text.strip()[:500]


def fetch() -> tuple:
    articles = []
    errors = []

    yesterday = datetime.utcnow() - timedelta(days=1)

    for source_name, url in FEEDS.items():

        if not url or url.startswith("<"):
            continue

        try:

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; daily-news-bot/1.0)"
                )
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

            response.encoding = "utf-8"

            feed = feedparser.parse(
                response.content
            )


            if feed.bozo:
                print(
                    f"⚠️ RSS 파싱 경고 - {source_name}: "
                    f"{feed.bozo_exception}"
                )


            for entry in feed.entries[:20]:

                title = entry.get(
                    "title",
                    ""
                ).strip()

                link = entry.get(
                    "link",
                    ""
                ).strip()


                if not title or not link:
                    continue


                published = (
                    entry.get("published_parsed")
                    or
                    entry.get("updated_parsed")
                )


                if published:

                    pub_date = datetime(
                        *published[:6]
                    )

                    # 오래된 뉴스 제거
                    # 단, 인사이트/리포트 계열은 허용
                    evergreen_sources = [
                        "McKinsey Insights",
                        "BCG Insights",
                        "PwC strategy+business",
                        "SSIR",
                        "PitchBook News",
                        "Impact Alpha",
                        "Climate Home News",
                        "The Batch",
                    ]

                    if (
                        pub_date < yesterday
                        and source_name not in evergreen_sources
                    ):
                        continue


                    date_str = pub_date.strftime(
                        "%Y-%m-%d"
                    )

                else:
                    date_str = "Unknown date"



                description = clean_html(
                    entry.get("summary")
                    or
                    entry.get("description")
                    or ""
                )


                articles.append(
                    {
                        "title": title,
                        "link": link,
                        "date": date_str,
                        "source": source_name,
                        "region": source_region(source_name),
                        "description": description,
                    }
                )


        except Exception as e:

            errors.append(
                f"{source_name} ({url}): {str(e)}"
            )


    return articles, errors
