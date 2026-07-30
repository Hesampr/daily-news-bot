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


def extract_gnews(entry, raw_title: str, feed_name: str):
    """Google News: 실제 언론사명(entry.source.title) 우선 사용 + 제목 끝 '- 언론사' 제거.
    실패 시 제목의 '- 언론사' 분리, 그것도 없으면 피드명 반환."""
    outlet = ""
    src = entry.get("source")
    if isinstance(src, dict):
        outlet = (src.get("title") or "").strip()

    title = raw_title.strip()
    # 제목이 '... - 언론사' 로 끝나면 접미어 제거
    if outlet and title.endswith(" - " + outlet):
        title = title[: -len(" - " + outlet)].strip()
    elif " - " in title:
        head, tail = title.rsplit(" - ", 1)
        if head.strip() and 1 <= len(tail) <= 40 and "\n" not in tail:
            title = head.strip()
            outlet = outlet or tail.strip()

    return title, (outlet or feed_name)


def fetch() -> tuple:
    articles = []
    errors = []

    yesterday = datetime.utcnow() - timedelta(days=1)

    for source_name, url in FEEDS.items():

        if not url or url.startswith("<"):
            continue

        is_gnews = "news.google.com" in url    # ✅ Google News 피드 여부

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

                raw_title = entry.get(
                    "title",
                    ""
                ).strip()

                link = entry.get(
                    "link",
                    ""
                ).strip()


                if not raw_title or not link:
                    continue

                # ✅ Google News: '제목 - 언론사' 분리해서 실제 언론사를 source 로.
                #    일반 RSS: 제목 그대로, source 는 피드명.
                if is_gnews:
                    title, display_source = extract_gnews(entry, raw_title, source_name)
                else:
                    title = raw_title
                    display_source = source_name


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
                        "source": display_source,   # ✅ 실제 언론사(가능 시) / 아니면 피드명
                        "feed": source_name,        # 라우팅/지역 판별용 원 피드명
                        "region": source_region(source_name),
                        "description": description,
                    }
                )


        except Exception as e:

            errors.append(
                f"{source_name} ({url}): {str(e)}"
            )


    return articles, errors
