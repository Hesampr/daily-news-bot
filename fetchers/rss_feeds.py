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


def split_google_news_title(raw_title: str, feed_name: str):
    """Google News 제목 '진짜 제목 - 언론사' → (제목, 언론사) 분리.
    분리 실패 시 (원제목, 피드명) 반환."""
    if " - " in raw_title:
        head, tail = raw_title.rsplit(" - ", 1)
        outlet = tail.strip()
        # 언론사명은 보통 짧다(과잉 분리 방지: 1~40자, 줄바꿈 없음)
        if head.strip() and 1 <= len(outlet) <= 40 and "\n" not in outlet:
            return head.strip(), outlet
    return raw_title.strip(), feed_name


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
                    title, display_source = split_google_news_title(raw_title, source_name)
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
