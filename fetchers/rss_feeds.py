import re
import socket
import requests
import feedparser
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


def clean_xml(content: bytes) -> str:
    """
    깨진 RSS XML 문자 제거
    """
    text = content.decode(
        "utf-8",
        errors="ignore"
    )

    # XML 파싱 깨뜨리는 제어문자 제거
    text = re.sub(
        r"[\x00-\x08\x0B\x0C\x0E-\x1F]",
        "",
        text
    )

    # escape 안 된 & 처리
    text = re.sub(
        r"&(?!amp;|lt;|gt;|quot;|apos;)",
        "&amp;",
        text
    )

    return text



def fetch() -> tuple:
    articles = []
    errors = []

    yesterday = datetime.utcnow() - timedelta(days=1)


    for source_name, url in FEEDS.items():

        if not url or url.startswith("<"):
            continue


        try:

            headers = {
                "User-Agent":
                "Mozilla/5.0 (compatible; daily-news-bot/1.0)"
            }


            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

            response.raise_for_status()


            xml = clean_xml(
                response.content
            )


            feed = feedparser.parse(xml)


            if feed.bozo:
                print(
                    f"⚠️ RSS 파싱 경고 - {source_name}: "
                    f"{feed.bozo_exception}"
                )


            for entry in feed.entries[:15]:

                title = (
                    entry.get("title", "")
                    .strip()
                )

                link = (
                    entry.get("link", "")
                    .strip()
                )


                if not title or not link:
                    continue



                published = (
                    entry.get("published_parsed")
                    or entry.get("updated_parsed")
                )


                if published:

                    pub_date = datetime(
                        *published[:6]
                    )

                    # MBB/Big4/인사이트 계열은 오래된 글 허용
                    evergreen_sources = [
                        "McKinsey Insights",
                        "BCG Insights",
                        "PwC strategy+business",
                        "SSIR",
                        "PitchBook News",
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



                description = (
                    entry.get("summary")
                    or entry.get("description")
                    or ""
                )


                description = re.sub(
                    r"<[^>]+>",
                    "",
                    description
                )


                description = (
                    description
                    .strip()
                    [:500]
                )



                articles.append({

                    "title": title,

                    "link": link,

                    "date": date_str,

                    "source": source_name,

                    "region": source_region(
                        source_name
                    ),

                    "description": description,

                })



        except Exception as e:

            errors.append(
                f"{source_name} ({url}): {str(e)}"
            )



    return articles, errors
