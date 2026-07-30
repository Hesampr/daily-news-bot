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

# ✅ Google News 리다이렉트 링크(news.google.com/rss/articles/CBMi..., 300자+)를
#    원문 URL로 디코딩 → 슬랙 메시지 길이 급감(분할 방지) + 원문 직링크.
#    미설치/실패 시 원 링크 유지(안전). requirements.txt 에 googlenewsdecoder 추가 필요.
try:
    from googlenewsdecoder import gnewsdecoder
except ImportError:
    gnewsdecoder = None

_GN_URL_CACHE = {}


def resolve_gnews_url(url: str) -> str:
    if not url or "news.google.com" not in url or gnewsdecoder is None:
        return url
    if url in _GN_URL_CACHE:
        return _GN_URL_CACHE[url]
    out = url
    try:
        d = gnewsdecoder(url)
        if isinstance(d, dict) and d.get("status") and d.get("decoded_url"):
            out = d["decoded_url"]
    except Exception:
        out = url
    _GN_URL_CACHE[url] = out
    return out


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
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0 Safari/537.36"
                ),
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
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

            # ✅ 파싱 실패(bozo+기사0) 시: 불법 XML 문자 제거 후 1회 재시도
            #    (한경/PwC 등 'not well-formed / invalid token' 구제)
            if feed.bozo and not feed.entries:
                cleaned_text = response.content.decode("utf-8", errors="ignore")
                cleaned_text = re.sub(
                    r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", cleaned_text
                )
                feed = feedparser.parse(cleaned_text)

            if feed.bozo and not feed.entries:
                print(
                    f"⚠️ RSS 파싱 실패(기사 0건) - {source_name}: "
                    f"{feed.bozo_exception}"
                )
            elif feed.bozo:
                print(
                    f"⚠️ RSS 파싱 경고(일부 수집) - {source_name}: "
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
                gnews_link = ""
                if is_gnews:
                    title, display_source = extract_gnews(entry, raw_title, source_name)
                    gnews_link = link               # ✅ 디코딩 전 원링크 보존(seen 이중키)
                    link = resolve_gnews_url(link)
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
                        "gnews_link": gnews_link,
                        "description": description,
                    }
                )


        except Exception as e:

            errors.append(
                f"{source_name} ({url}): {str(e)}"
            )


    return articles, errors
